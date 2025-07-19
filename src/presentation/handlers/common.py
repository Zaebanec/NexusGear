from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

common_router = Router()

def get_main_menu_keyboard():
    """Создает и возвращает клавиатуру главного меню."""
    builder = ReplyKeyboardBuilder()
    builder.button(text="🛍️ Каталог")
    # Сюда можно добавить другие кнопки, например "🛒 Корзина", "👤 Профиль"
    builder.adjust(1) # Располагаем кнопки по одной в ряд
    return builder.as_markup(resize_keyboard=True)


@common_router.message(CommandStart())
async def start_handler(message: Message):
    """
    Обработчик команды /start. Отправляет приветственное сообщение
    и клавиатуру главного меню.
    """
    # TODO: Интегрировать UserService для регистрации пользователя
    await message.answer(
        f"Добро пожаловать в NEXUS Gear, {message.from_user.full_name}!",
        reply_markup=get_main_menu_keyboard(),
    )