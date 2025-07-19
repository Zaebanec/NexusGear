from aiogram import Router  # Изменяем импорт
from dishka.async_container import AsyncContainer
from dishka.integrations.aiogram import setup_dishka

def setup_dishka_for_router(container: AsyncContainer, router: Router):
    """
    Применяет DI-middleware к КОНКРЕТНОМУ роутеру.
    """
    setup_dishka(container=container, router=router)