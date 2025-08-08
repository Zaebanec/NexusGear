# src/presentation/bot.py - ФИНАЛЬНАЯ ВЕРСИЯ

import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiohttp import web
from dishka import make_async_container

from src.infrastructure.config import settings
from src.infrastructure.di.providers import (
    AIProvider,
    ConfigProvider,
    DbProvider,
    MemoryProvider,
    RepoProvider,
    ServiceProvider,
    TelegramProvider,  # добавили
)
from src.infrastructure.logging.setup import setup_logging
from src.presentation.handlers.ai_consultant import ai_router
from src.presentation.handlers.common import common_router
from src.presentation.middlewares import LoggingMiddleware
from src.presentation.web.app import setup_app


def main():
    setup_logging()
    container = make_async_container(
        ConfigProvider(),
        DbProvider(),
        MemoryProvider(),
        RepoProvider(),
        AIProvider(),
        TelegramProvider(),  # теперь бот будет доступен в контейнере
        ServiceProvider(),   # и notifier корректно создастся
    )
    bot = Bot(
        token=settings.bot.token.get_secret_value(),
        default=DefaultBotProperties(parse_mode="HTML")
    )
    dp = Dispatcher(dishka_container=container)

    dp.update.outer_middleware(LoggingMiddleware())
    dp.include_router(common_router)
    dp.include_router(ai_router)

    app = setup_app(dishka_container=container, bot=bot, dispatcher=dp)

    logging.info("Запуск веб-сервера в режиме webhook...")
    web.run_app(
        app,
        host="0.0.0.0",
        port=8080,
    )