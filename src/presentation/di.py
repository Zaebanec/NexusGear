from aiogram import Dispatcher
from dishka import make_async_container
from dishka.integrations.aiogram import setup_dishka

# --- НАЧАЛО ИЗМЕНЕНИЙ ---
from src.infrastructure.di.providers import ConfigProvider, DbProvider, RepoProvider
# --- КОНЕЦ ИЗМЕНЕНИЙ ---


def setup_di(dispatcher: Dispatcher):
    """
    Настраивает DI-контейнер dishka и интегрирует его с aiogram.
    """
    # --- НАЧАЛО ИЗМЕНЕНИЙ ---
    # Создаем контейнер, передавая ему все наши провайдеры
    container = make_async_container(
        ConfigProvider(),
        DbProvider(),
        RepoProvider(), # <-- Регистрируем новый провайдер
        # Здесь будут добавляться другие провайдеры (сервисы)
    )
    # --- КОНЕЦ ИЗМЕНЕНИЙ ---

    # Интегрируем контейнер с диспетчером aiogram.
    setup_dishka(container=container, router=dispatcher)