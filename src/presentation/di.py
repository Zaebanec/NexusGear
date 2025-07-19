from aiogram import Dispatcher
from dishka import make_async_container
from dishka.integrations.aiogram import setup_dishka

from src.infrastructure.di.providers import (
    ConfigProvider,
    DbProvider,
    RepoProvider,
    ServiceProvider,  # <-- Импортируем новый провайдер
)

def setup_di(dispatcher: Dispatcher):
    container = make_async_container(
        ConfigProvider(),
        DbProvider(),
        RepoProvider(),
        ServiceProvider(),  # <-- Регистрируем новый провайдер
    )
    setup_dishka(container=container, router=dispatcher)