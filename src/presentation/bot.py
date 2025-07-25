import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiohttp import web
from dishka import make_async_container
from src.infrastructure.logging.setup import setup_logging
from src.infrastructure.config import settings
from src.infrastructure.di.providers import (
    ConfigProvider, DbProvider, MemoryProvider, RepoProvider, ServiceProvider,
)
from src.presentation.handlers.catalog import catalog_router
from src.presentation.handlers.common import common_router
from src.presentation.handlers.cart import cart_router
from src.presentation.web.app import setup_app

async def main():
    setup_logging()
    container = make_async_container(
        ConfigProvider(), DbProvider(), MemoryProvider(), RepoProvider(), ServiceProvider()
    )
    bot = Bot(
        token=settings.bot.token.get_secret_value(),
        default=DefaultBotProperties(parse_mode="HTML")
    )
    dp = Dispatcher(dishka_container=container)
    dp.include_router(common_router)
    dp.include_router(catalog_router)
    dp.include_router(cart_router)
    app = setup_app(dishka_container=container)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    try:
        logging.info("Запуск веб-сервера и Telegram-бота...")
        await site.start()
        await dp.start_polling(bot)
    finally:
        logging.info("Остановка...")
        await runner.cleanup()
        await container.close()
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Приложение остановлено.")
