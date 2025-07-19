import asyncio
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
# --- НАЧАЛО ИСПРАВЛЕНИЯ ---
# 1. Удаляем импорт ненужной функции
# from src.presentation.di import setup_di
# --- КОНЕЦ ИСПРАВЛЕНИЯ ---
from src.presentation.handlers.catalog import catalog_router
from src.presentation.handlers.common import common_router
from src.presentation.web.app import setup_app


async def main():
    logging.basicConfig(level=logging.INFO)
    container = make_async_container(
        ConfigProvider(),
        DbProvider(),
        MemoryProvider(),
        RepoProvider(),
        ServiceProvider()
    )

    bot = Bot(
        token=settings.bot.token.get_secret_value(),
        default=DefaultBotProperties(parse_mode="HTML")
    )

    # --- НАЧАЛО ИСПРАВЛЕНИЯ ---
    # 2. Передаем контейнер напрямую в Dispatcher.
    #    Это и есть наша новая стратегия.
    dp = Dispatcher(dishka_container=container)
    # --- КОНЕЦ ИСПРАВЛЕНИЯ ---
    
    dp.include_router(common_router)
    dp.include_router(catalog_router)

    # --- НАЧАЛО ИСПРАВЛЕНИЯ ---
    # 3. Удаляем вызов ненужной функции
    # setup_di(dp, container)
    # --- КОНЕЦ ИСПРАВЛЕНИЯ ---

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