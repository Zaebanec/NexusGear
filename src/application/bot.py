import asyncio
import logging

from aiogram import Bot, Dispatcher

from src.infrastructure.config import settings
from src.presentation.di import setup_di


async def main():
    """Основная функция для запуска бота."""
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=settings.bot.get_secret_value())
    dp = Dispatcher()

    # Настраиваем и внедряем DI-контейнер
    setup_di(dp)

    # Здесь будет регистрация роутеров
    # dp.include_router(...)

    # Запускаем поллинг
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")