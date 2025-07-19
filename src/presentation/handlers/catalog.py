from aiogram import Dispatcher, F, Router
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dishka import Scope

from src.application.services.catalog import CategoryService, ProductService

class CategoryCallbackFactory(CallbackData, prefix="category"):
    id: int
    name: str

catalog_router = Router()

@catalog_router.message(F.text == "🛍️ Каталог")
async def show_categories(message: Message, dispatcher: Dispatcher):
    container = dispatcher["dishka_container"]
    # --- ИЗМЕНЕНИЕ ---
    async with container(scope=Scope.REQUEST) as request_container:
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
    dispatcher: Dispatcher,
):
    container = dispatcher["dishka_container"]
    # --- ИЗМЕНЕНИЕ ---
    async with container(scope=Scope.REQUEST) as request_container:
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
            await query.message.answer(card)