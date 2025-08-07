# src/presentation/handlers/cart.py - ФИНАЛЬНАЯ ВЕРСИЯ С TWA

import json
import logging
import traceback
from decimal import Decimal

from aiogram import F, Router
from aiogram.types import (  # <-- Импортируем WebAppInfo
    CallbackQuery,
    Message,
    PreCheckoutQuery,  # <-- НОВЫЙ ИМПОРТ
    WebAppInfo,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dishka import AsyncContainer, Scope

from src.application.contracts.cart.cart_repository import ICartRepository
from src.application.contracts.persistence.uow import IUnitOfWork
from src.application.services.order_service import OrderService
from src.domain.entities.cart_item import CartItem
from src.infrastructure.config import settings  # <-- Импортируем настройки для URL

from .catalog import AddProductCallbackFactory

cart_router = Router()

# Этот CallbackData больше не нужен, но оставим его, если понадобится в будущем
# class CreateOrderCallbackFactory(CallbackData, prefix="create_order"):
#     pass

@cart_router.pre_checkout_query()
async def pre_checkout_query_handler(query: PreCheckoutQuery):
    """
    Пустой обработчик для подтверждения готовности принять платеж.
    Это необходимо для некоторых TWA-взаимодействий.
    """
    await query.answer(ok=True)

@cart_router.callback_query(AddProductCallbackFactory.filter())
async def add_product_to_cart(
    query: CallbackQuery,
    callback_data: AddProductCallbackFactory,
    dishka_container: AsyncContainer,
):
    async with dishka_container(scope=Scope.REQUEST) as request_container:
        cart_repo = await request_container.get(ICartRepository)
        item_to_add = CartItem(
            product_id=callback_data.id, name=callback_data.name,
            price=callback_data.price, quantity=1,
        )
        await cart_repo.add_item(user_id=query.from_user.id, item=item_to_add)
    
    await query.answer(f'Товар "{callback_data.name}" добавлен в корзину!', show_alert=True)

@cart_router.message(F.text == "🛒 Корзина")
async def view_cart(message: Message, dishka_container: AsyncContainer):
    async with dishka_container(scope=Scope.REQUEST) as request_container:
        cart_repo = await request_container.get(ICartRepository)
        items = await cart_repo.get_by_user_id(user_id=message.from_user.id)

    if not items:
        await message.answer("Ваша корзина пуста.")
        return

    cart_text = "<b>Ваша корзина:</b>\n\n"
    total_amount = Decimal("0")
    for i, item in enumerate(items, 1):
        item_total = item.price * item.quantity
        cart_text += f"{i}. {item.name}\n   {item.quantity} шт. x {item.price} руб. = {item_total} руб.\n"
        total_amount += item_total
    
    cart_text += f"\n<b>Итого: {total_amount} руб.</b>"
    
    # --- НАЧАЛО ИЗМЕНЕНИЯ: Кнопка теперь открывает WebApp ---
    builder = InlineKeyboardBuilder()
    # Формируем URL для нашего TWA
    web_app_url = f"{settings.app.base_url}/order"
    builder.button(
        text="✅ Оформить заказ", 
        web_app=WebAppInfo(url=web_app_url)
    )
    # --- КОНЕЦ ИЗМЕНЕНИЯ ---
    
    await message.answer(cart_text, reply_markup=builder.as_markup())

# --- НАЧАЛО ИЗМЕНЕНИЯ: Новый хендлер для данных из TWA ---
# Он срабатывает, когда пользователь нажимает главную кнопку в TWA
@cart_router.message(F.web_app_data)
async def web_app_data_received(message: Message, dishka_container: AsyncContainer):
    telegram_id = message.from_user.id

    # Данные приходят в виде JSON-строки
    data = json.loads(message.web_app_data.data)
    # Можно добавить валидацию данных (например, через Pydantic)

    # Выводим полученные данные для отладки
    await message.answer(
        f"Спасибо! Ваши данные для заказа получены:\n"
        f"<b>ФИО:</b> {data.get('full_name')}\n"
        f"<b>Телефон:</b> {data.get('phone')}\n"
        f"<b>Адрес:</b> {data.get('address')}\n\n"
        f"Создаем ваш заказ..."
    )

    # Используем ту же логику создания заказа, что и раньше
    async with dishka_container(scope=Scope.REQUEST) as request_container:
        uow = await request_container.get(IUnitOfWork)
        order_service = await request_container.get(OrderService)

        try:
            async with uow.atomic():
                order = await order_service.create_order(telegram_id=telegram_id)

            # Добавляем детали из формы к сообщению об успехе
            await message.answer(
                f"✅ Ваш заказ №{order.id} успешно создан и будет доставлен по адресу: {data.get('address')}.\n"
                f"Ожидайте звонка на номер {data.get('phone')} для подтверждения."
            )

        except ValueError as e:
            logging.warning(f"Ошибка создания заказа для user {telegram_id}: {e}")
            await message.answer(str(e))
        except Exception as e:
            logging.error(f"Критическая ошибка при создании заказа для user {telegram_id}: {e}")
            traceback.print_exc()
            await message.answer("Произошла непредвиденная ошибка при создании заказа.")
# --- КОНЕЦ ИЗМЕНЕНИЯ ---

# Старый хендлер create_order удален, так как он больше не используется.
