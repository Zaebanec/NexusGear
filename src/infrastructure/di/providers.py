from typing import AsyncGenerator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.infrastructure.config import Settings, settings


class ConfigProvider(Provider):
    """
    Провайдер для доступа к конфигурации приложения.
    """
    @provide(scope=Scope.APP)
    def get_config(self) -> Settings:
        return settings


class DbProvider(Provider):
    """
    Провайдер для зависимостей базы данных.
    Управляет жизненным циклом движка, фабрики сессий и самих сессий.
    """
    scope = Scope.APP

    @provide
    def get_engine(self, config: Settings) -> AsyncEngine:
        """Создает и возвращает асинхронный движок SQLAlchemy."""
        return create_async_engine(
            url=config.db.url,
            echo=False, # В продакшене лучше отключать
        )

    @provide
    def get_session_factory(
        self, engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        """Создает и возвращает фабрику сессий."""
        return async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> AsyncGenerator[AsyncSession, None]:
        """
        Предоставляет сессию БД для одного запроса (например, одного сообщения).
        Сессия автоматически закрывается после завершения обработки.
        """
        async with session_factory() as session:
            yield session