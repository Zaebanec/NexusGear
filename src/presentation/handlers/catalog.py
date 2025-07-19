from aiogram import F, Router
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dishka.integrations.aiogram import FromDishka

from src.application.services.catalog import CategoryService, ProductService

# --- Фабрика для Callback'ов Категорий ---
class CategoryCallbackFactory(CallbackData, prefix="category"):
    id: int
    name: str # Полезно для логирования или отображения

# --- Роутер для Каталога ---
catalog_router = Router()


@catalog_router.message(F.text == "🛍️ Каталог")
async def show_categories(
    message: Message, category_service: FromDishka[CategoryService]
):
    """
    Обработчик для отображения списка категорий в виде инлайн-кнопок.
    """
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
    builder.adjust(2)  # Располагаем кнопки по 2 в ряд

    await message.answer(
        "Выберите категорию:", reply_markup=builder.as_markup()
    )


@catalog_router.callback_query(CategoryCallbackFactory.filter())
async def show_products(
    query: CallbackQuery,
    callback_data: CategoryCallbackFactory,
    product_service: FromDishka[ProductService],
):
    """
    Обработчик для отображения товаров выбранной категории.
    """
    await query.answer(f"Загружаю товары из '{callback_data.name}'...")

    products = await product_service.get_by_category(callback_data.id)

    if not products:
        await query.message.answer("В этой категории пока нет товаров.")
        return

    # Отправляем товары отдельными сообщениями для наглядности
    for product in products:
        card = (
            f"<b>{product.name}</b>\n"
            f"<i>Цена: {product.price} руб.</i>\n\n"
            f"{product.description}"
        )
        # TODO: Добавить фото и кнопку "Купить"
        await query.message.answer(card, parse_mode="HTML")