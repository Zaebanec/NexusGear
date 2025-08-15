# src/presentation/handlers/common.py - ФИНАЛЬНАЯ ВЕРСИЯ

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder # <-- Изменяем импорт
from dishka import AsyncContainer, Scope

from src.application.services.user_service import UserService
from src.infrastructure.config import settings

common_router = Router()

# ReplyKeyboardBuilder и get_main_menu_keyboard() больше не нужны

@common_router.message(CommandStart())
async def start_handler(message: Message, dishka_container: AsyncContainer):
    """
    Обработчик команды /start. Регистрирует пользователя и отправляет
    приветственное сообщение с кнопкой для открытия магазина (TWA на Vue).
    """
    # Защита от отсутствующего from_user (mypy)
    if message.from_user is None:
        return

    async with dishka_container(scope=Scope.REQUEST) as request_container:
        user_service = await request_container.get(UserService)
        await user_service.register_user_if_not_exists(
            telegram_id=message.from_user.id,
            full_name=message.from_user.full_name,
            username=message.from_user.username,
        )
    
    # --- НАЧАЛО ИСПРАВЛЕНИЯ: Создаем инлайн-кнопку для открытия Vue App ---
    builder = InlineKeyboardBuilder()
    base = settings.app.base_url.rstrip('/')
    store_url = f"{base}/"
    admin_url = f"{base}/admin"
    builder.button(text="🛍️ Открыть магазин", web_app=WebAppInfo(url=store_url))
    builder.button(text="🛠 Админка", web_app=WebAppInfo(url=admin_url))
    # по одному на строку, чтобы Telegram гарантированно отрисовал обе
    builder.adjust(1)
    # --- КОНЕЦ ИСПРАВЛЕНИЯ ---

    await message.answer(
        f"Добро пожаловать в NEXUS Gear, {message.from_user.full_name}!",
        reply_markup=builder.as_markup(),
    )