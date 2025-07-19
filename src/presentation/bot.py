import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiohttp import web
from dishka import make_async_container

from src.infrastructure.config import settings
from src.infrastructure.di.providers import (
    ConfigProvider,
    DbProvider,
    RepoProvider,
    ServiceProvider,
)
from src.presentation.di import setup_di
from src.presentation.web.app import setup_app


async def main():
    """Основная функция для параллельного запуска бота и веб-сервера."""
    logging.basicConfig(level=logging.INFO)

    # --- Создание DI-контейнера ---
    container = make_async_container(
        ConfigProvider(),
        DbProvider(),
        RepoProvider(),
        ServiceProvider(),
    )

    # --- Настройка Telegram-бота ---
    bot = Bot(token=settings.bot.get_secret_value())
    dp = Dispatcher()
    # Интегрируем DI с Aiogram
    setup_di(dp, container)

    # --- Настройка веб-сервера AIOHTTP ---
    # Передаем тот же контейнер в веб-приложение
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