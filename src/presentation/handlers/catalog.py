# src/presentation/handlers/catalog.py - ИСПРАВЛЕННАЯ ВЕРСИЯ

from decimal import Decimal

from aiogram import F, Router
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dishka import AsyncContainer, Scope  # <-- Импортируем AsyncContainer

from src.application.services.catalog import CategoryService, ProductService


class CategoryCallbackFactory(CallbackData, prefix="category"):
    id: int
    name: str

class AddProductCallbackFactory(CallbackData, prefix="add_product"):
    id: int
    name: str
    price: Decimal

catalog_router = Router()

@catalog_router.message(F.text == "🛍️ Каталог")
async def show_categories(message: Message, dishka_container: AsyncContainer): # <-- ИЗМЕНЕНИЕ
    """
    Обработчик для отображения списка категорий в виде инлайн-кнопок.
    """
    async with dishka_container(scope=Scope.REQUEST) as request_container: # <-- ИЗМЕНЕНИЕ
        category_service = await request_container.get(CategoryService)

        categories = await category_service.get_all()
        if not categories:
            await message.answer("К сожалению, сейчас нет доступных категорий.")
            return

        builder = InlineKeyboardBuilder()
        for category in categories:
            builder.button(
                text=category.name,
                callback_data=CategoryCallbackFactory(id=category.id, name=category.name),
            )
        builder.adjust(2)

        await message.answer(
            "Выберите категорию:", reply_markup=builder.as_markup()
        )


@catalog_router.callback_query(CategoryCallbackFactory.filter())
async def show_products(
    query: CallbackQuery,
    callback_data: CategoryCallbackFactory,
    dishka_container: AsyncContainer, # <-- ИЗМЕНЕНИЕ
):
    """
    Обработчик для отображения товаров выбранной категории.
    """
    async with dishka_container(scope=Scope.REQUEST) as request_container: # <-- ИЗМЕНЕНИЕ
        product_service = await request_container.get(ProductService)

        products = await product_service.get_by_category(callback_data.id)
        if not products:
            await query.message.answer("В этой категории пока нет товаров.")
            await query.answer()
            return

        await query.answer(f"Загружаю товары из '{callback_data.name}'...")
        for product in products:
            card = (
                f"<b>{product.name}</b>\n"
                f"<i>Цена: {product.price} руб.</i>\n\n"
                f"{product.description}"
            )
            builder = InlineKeyboardBuilder()
            builder.button(
                text="➕ Добавить в корзину",
                callback_data=AddProductCallbackFactory(
                    id=product.id, name=product.name, price=product.price
                ),
            )
            await query.message.answer(card, reply_markup=builder.as_markup())