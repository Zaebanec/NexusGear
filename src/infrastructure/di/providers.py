from typing import AsyncGenerator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.application.interfaces.repositories.category_repository import (
    ICategoryRepository,
)
from src.application.interfaces.repositories.product_repository import (
    IProductRepository,
)
from src.application.interfaces.repositories.user_repository import IUserRepository
from src.infrastructure.config import Settings, settings
from src.infrastructure.database.repositories.category_repository import (
    CategoryRepository,
)
from src.infrastructure.database.repositories.product_repository import (
    ProductRepository,
)
from src.infrastructure.database.repositories.user_repository import UserRepository


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
    """
    scope = Scope.APP

    @provide
    def get_engine(self, config: Settings) -> AsyncEngine:
        """Создает и возвращает асинхронный движок SQLAlchemy."""
        return create_async_engine(url=config.db.url)

    @provide
    def get_session_factory(
        self, engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        """Создает и возвращает фабрику сессий."""
        return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> AsyncGenerator[AsyncSession, None]:
        """Предоставляет сессию БД для одного запроса."""
        async with session_factory() as session:
            yield session


# --- НАЧАЛО ИЗМЕНЕНИЙ ---

class RepoProvider(Provider):
    """
    Провайдер для репозиториев. Связывает интерфейсы с их реализациями.
    """
    scope = Scope.REQUEST

    @provide
    def get_user_repo(self, session: AsyncSession) -> IUserRepository:
        return UserRepository(session)

    @provide
    def get_category_repo(self, session: AsyncSession) -> ICategoryRepository:
        return CategoryRepository(session)

    @provide
    def get_product_repo(self, session: AsyncSession) -> IProductRepository:
        return ProductRepository(session)

# --- КОНЕЦ ИЗМЕНЕНИЙ ---