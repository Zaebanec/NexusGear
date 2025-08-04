# src/presentation/web/app.py - ФИНАЛЬНАЯ ВЕРСИЯ

import logging

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiohttp import web
from dishka.async_container import AsyncContainer

from src.infrastructure.config import settings

WEBHOOK_PATH = "/webhook"
# Сформируем URL для вебхука один раз
WEBHOOK_URL = f"{settings.app.base_url}{WEBHOOK_PATH}"

async def on_startup(app: web.Application):
    bot: Bot = app["bot"]
    await bot.set_webhook(f"{settings.app.base_url}{WEBHOOK_PATH}", drop_pending_updates=True)
    logging.info(f"Webhook установлен на: {settings.app.base_url}{WEBHOOK_PATH}")

async def on_shutdown(app: web.Application):
    bot: Bot = app["bot"]
    await bot.delete_webhook()
    logging.info("Webhook удален.")

async def webhook_handler(request: web.Request) -> web.Response:
    bot: Bot = request.app["bot"]
    dispatcher: Dispatcher = request.app["dispatcher"]
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dispatcher.feed_update(bot=bot, update=update)
    return web.Response()

def setup_app(
    dishka_container: AsyncContainer, bot: Bot, dispatcher: Dispatcher
) -> web.Application:
    app = web.Application()
    app["dishka_container"] = dishka_container
    app["bot"] = bot
    app["dispatcher"] = dispatcher

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    return app