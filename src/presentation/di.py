from dishka import make_async_container
from dishka.integrations.aiogram import setup_dishka
from aiogram import Dispatcher

from src.infrastructure.di.providers import ConfigProvider, DbProvider


def setup_di(dispatcher: Dispatcher):
    """
    Настраивает DI-контейнер dishka и интегрирует его с aiogram.
    """
    # Создаем контейнер, передавая ему все наши провайдеры
    container = make_async_container(
        ConfigProvider(),
        DbProvider(),
        # Здесь будут добавляться другие провайдеры (сервисы, репозитории)
    )

    # Интегрируем контейнер с диспетчером aiogram.
    # Это добавит middleware, которое будет создавать REQUEST-скоуп
    # для каждого входящего сообщения и внедрять зависимости в хендлеры.
    setup_dishka(container=container, router=dispatcher)