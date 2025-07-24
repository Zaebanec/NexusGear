from aiogram import Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from dishka import Scope

from src.application.services.user_service import UserService

common_router = Router()

def get_main_menu_keyboard():
    """
    Создает и возвращает клавиатуру главного меню.
    """
    builder = ReplyKeyboardBuilder()
    builder.button(text="🛍️ Каталог")
    builder.button(text="🛒 Корзина")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


@common_router.message(CommandStart())
async def start_handler(message: Message, dispatcher: Dispatcher):
    """
    Обработчик команды /start. Регистрирует пользователя и отправляет
    приветственное сообщение с клавиатурой главного меню.
    """
    container = dispatcher["dishka_container"]
    async with container(scope=Scope.REQUEST) as request_container:
        user_service = await request_container.get(UserService)
        await user_service.register_user_if_not_exists(
            telegram_id=message.from_user.id,
            full_name=message.from_user.full_name,
            username=message.from_user.username,
        )
    
    await message.answer(
        f"Добро пожаловать в NEXUS Gear, {message.from_user.full_name}!",
        reply_markup=get_main_menu_keyboard(),
    )