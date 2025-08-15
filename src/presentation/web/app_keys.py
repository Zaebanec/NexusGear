# src/presentation/web/app_keys.py

from __future__ import annotations

from aiohttp.web_app import AppKey
from aiogram import Bot, Dispatcher
from dishka import AsyncContainer


APP_DISHKA_CONTAINER: AppKey[AsyncContainer] = AppKey("dishka_container")
APP_BOT: AppKey[Bot] = AppKey("bot")
APP_DISPATCHER: AppKey[Dispatcher] = AppKey("dispatcher")


