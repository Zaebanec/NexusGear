# src/presentation/bot.py - ФИНАЛЬНАЯ ВЕРСИЯ

import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiohttp import web
from dishka import make_async_container

from src.infrastructure.config import settings
from src.infrastructure.di.providers import (
    ConfigProvider,
    DbProvider,
    MemoryProvider,
    RepoProvider,
    ServiceProvider,
)
from src.infrastructure.logging.setup import setup_logging
from src.presentation.handlers.cart import cart_router
from src.presentation.handlers.catalog import catalog_router
from src.presentation.handlers.common import common_router
from src.presentation.middlewares import LoggingMiddleware
from src.presentation.web.app import setup_app


def main(): # <-- Убираем async, так как run_app - синхронный
    setup_logging()
    container = make_async_container(
        ConfigProvider(), DbProvider(), MemoryProvider(), RepoProvider(), ServiceProvider(),
    )
    bot = Bot(
        token=settings.bot.token.get_secret_value(),
        default=DefaultBotProperties(parse_mode="HTML")
    )
    dp = Dispatcher(dishka_container=container)

    dp.update.outer_middleware(LoggingMiddleware())
    dp.include_router(common_router)
    dp.include_router(catalog_router)
    dp.include_router(cart_router)

    app = setup_app(dishka_container=container, bot=bot, dispatcher=dp)
    
    # --- НАЧАЛО ФИНАЛЬНОГО ИСПРАВЛЕНИЯ ---
    # web.run_app - это высокоуровневый, синхронный вызов,
    # который сам создает и управляет asyncio циклом.
    # Он автоматически вызовет наши хуки on_startup/on_shutdown.
    logging.info("Запуск веб-сервера в режиме webhook...")
    web.run_app(
        app,
        host="0.0.0.0",
        port=8080,
    )
    # --- КОНЕЦ ФИНАЛЬНОГО ИСПРАВЛЕНИЯ ---


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Приложение остановлено.")
