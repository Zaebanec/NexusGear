# src/presentation/handlers/cart.py - ЭТАЛОННАЯ ВЕРСИЯ

import logging
import traceback
from decimal import Decimal
from aiogram import Dispatcher, F, Router
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dishka import Scope

from src.application.contracts.cart.cart_repository import ICartRepository
from src.application.contracts.persistence.uow import IUnitOfWork # <-- ИМПОРТ
from src.application.interfaces.repositories.user_repository import IUserRepository
from src.application.services.order_service import OrderService
from src.domain.entities.cart_item import CartItem

from .catalog import AddProductCallbackFactory

cart_router = Router()

class CreateOrderCallbackFactory(CallbackData, prefix="create_order"):
    pass

@cart_router.callback_query(AddProductCallbackFactory.filter())
async def add_product_to_cart(
    query: CallbackQuery,
    callback_data: AddProductCallbackFactory,
    dispatcher: Dispatcher,
):
    container = dispatcher["dishka_container"]
    cart_repo = await container.get(ICartRepository)

    item_to_add = CartItem(
        product_id=callback_data.id, name=callback_data.name,
        price=callback_data.price, quantity=1,
    )
    await cart_repo.add_item(user_id=query.from_user.id, item=item_to_add)
    await query.answer(f'Товар "{callback_data.name}" добавлен в корзину!', show_alert=True)

@cart_router.message(F.text == "🛒 Корзина")
async def view_cart(message: Message, dispatcher: Dispatcher):
    container = dispatcher["dishka_container"]
    cart_repo = await container.get(ICartRepository)

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
    dispatcher: Dispatcher,
):
    telegram_id = query.from_user.id
    container = dispatcher["dishka_container"]

    async with container(scope=Scope.REQUEST) as request_container:
        # --- НАЧАЛО ИЗМЕНЕНИЯ: ЯВНОЕ УПРАВЛЕНИЕ ТРАНЗАКЦИЕЙ ---
        uow = await request_container.get(IUnitOfWork)
        user_repo = await request_container.get(IUserRepository)
        order_service = await request_container.get(OrderService)

        try:
            # Открываем транзакцию ЗДЕСЬ, на самом верхнем уровне
            async with uow.atomic():
                user = await user_repo.get_by_telegram_id(telegram_id)
                if not user:
                    # Это исключение вызовет автоматический rollback в uow.atomic()
                    raise ValueError("Пользователь не найден")

                # Вызываем сервис, который теперь работает в НАШЕЙ транзакции
                order = await order_service.create_order_from_cart(
                    internal_user_id=user.id,
                    telegram_id=telegram_id
                )
            
            # Если мы вышли из блока без ошибок, транзакция закоммичена
            await query.message.answer(f"✅ Ваш заказ №{order.id} успешно создан и ожидает оплаты.")
            await query.answer("Заказ создан!")

        except ValueError as e:
            # Отлавливаем наше бизнес-исключение
            logging.warning(f"Ошибка создания заказа: {e}")
            await query.answer("Ошибка: пользователь не найден. Пожалуйста, перезапустите бота командой /start.", show_alert=True)
        except Exception as e:
            traceback.print_exc()
            await query.answer("Произошла ошибка при создании заказа.", show_alert=True)