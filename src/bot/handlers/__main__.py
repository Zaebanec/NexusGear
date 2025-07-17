import asyncio
import logging

from aiogram import Bot, Dispatcher

from src.bot.core.config import settings
from src.bot.handlers import start

async def main():
    """
    Main function to configure and run the bot.
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logging.info("Starting bot...")

    # Initialize Bot and Dispatcher
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    # Include routers
    dp.include_router(start.router)

    # Delete webhook and start polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")