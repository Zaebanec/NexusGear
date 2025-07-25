# src/presentation/handlers/cart.py - УНИФИЦИРОВАННАЯ ВЕРСИЯ

import logging
import traceback
from decimal import Decimal

from aiogram import Dispatcher, F, Router
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dishka import AsyncContainer, Scope

from src.application.contracts.cart.cart_repository import ICartRepository
from src.application.contracts.persistence.uow import IUnitOfWork
from src.application.services.order_service import OrderService
from src.domain.entities.cart_item import CartItem

from .catalog import AddProductCallbackFactory

cart_router = Router()

class CreateOrderCallbackFactory(CallbackData, prefix="create_order"):
    pass

# --- ИСПРАВЛЕНИЕ: Хендлер приведен к каноническому виду ---
@cart_router.callback_query(AddProductCallbackFactory.filter())
async def add_product_to_cart(
    query: CallbackQuery,
    callback_data: AddProductCallbackFactory,
    dishka_container: AsyncContainer,
):
    # Используем канонический паттерн для получения зависимостей
    async with dishka_container(scope=Scope.REQUEST) as request_container:
        cart_repo = await request_container.get(ICartRepository)

        item_to_add = CartItem(
            product_id=callback_data.id, name=callback_data.name,
            price=callback_data.price, quantity=1,
        )
        await cart_repo.add_item(user_id=query.from_user.id, item=item_to_add)
    
    await query.answer(f'Товар "{callback_data.name}" добавлен в корзину!', show_alert=True)

# --- ИСПРАВЛЕНИЕ: Хендлер приведен к каноническому виду ---
@cart_router.message(F.text == "🛒 Корзина")
async def view_cart(message: Message, dishka_container: AsyncContainer):
    # Используем канонический паттерн для получения зависимостей
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
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Оформить заказ", callback_data=CreateOrderCallbackFactory())
    await message.answer(cart_text, reply_markup=builder.as_markup())

@cart_router.callback_query(CreateOrderCallbackFactory.filter())
async def create_order(
    query: CallbackQuery,
    callback_data: CreateOrderCallbackFactory,
    dishka_container: AsyncContainer,
):
    telegram_id = query.from_user.id

    async with dishka_container(scope=Scope.REQUEST) as request_container:
        uow = await request_container.get(IUnitOfWork)
        order_service = await request_container.get(OrderService)

        try:
            async with uow.atomic():
                # --- ИЗМЕНЕНИЕ: Мы передаем telegram_id, как и ожидает новый сервис ---
                order = await order_service.create_order(telegram_id=telegram_id)
            
            await query.message.answer(f"✅ Ваш заказ №{order.id} успешно создан и ожидает оплаты.")
            await query.answer("Заказ создан!")

        except ValueError as e:
            logging.warning(f"Ошибка создания заказа для user {telegram_id}: {e}")
            await query.answer(str(e), show_alert=True)
        except Exception as e:
            logging.error(f"Критическая ошибка при создании заказа для user {telegram_id}: {e}")
            traceback.print_exc()
            await query.answer("Произошла непредвиденная ошибка при создании заказа.", show_alert=True)