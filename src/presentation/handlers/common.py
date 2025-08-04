# src/presentation/handlers/common.py - ИСПРАВЛЕННАЯ ВЕРСИЯ

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from dishka import AsyncContainer, Scope  # <-- Импортируем AsyncContainer

from src.application.services.user_service import UserService

common_router = Router()

def get_main_menu_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="🛍️ Каталог")
    builder.button(text="🛒 Корзина")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


@common_router.message(CommandStart())
async def start_handler(message: Message, dishka_container: AsyncContainer): # <-- ИЗМЕНЕНИЕ
    """
    Обработчик команды /start. Регистрирует пользователя и отправляет
    приветственное сообщение с клавиатурой главного меню.
    """
    # --- ИЗМЕНЕНИЕ: Убираем получение container из dispatcher ---
    # async with dishka_container(...) теперь является стандартным паттерном
    async with dishka_container(scope=Scope.REQUEST) as request_container:
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