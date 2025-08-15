# src/infrastructure/di/providers.py — финальная версия

from typing import AsyncGenerator

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# --- Импорты Контрактов ---
from src.application.contracts.cart.cart_repository import ICartRepository
from src.application.contracts.notifications.notifier import INotifier
from src.application.contracts.persistence.uow import IUnitOfWork
from src.application.interfaces.repositories.category_repository import (
    ICategoryRepository,
)
from src.application.interfaces.repositories.product_repository import (
    IProductRepository,
)
from src.application.interfaces.repositories.user_repository import IUserRepository

# --- Импорты Сервисов ---
from src.application.services.ai_consultant import AIConsultantService
from src.application.services.catalog import CategoryService, ProductService
from src.application.services.order_service import OrderService
from src.application.services.user_service import UserService
from src.infrastructure.ai.gemini_client import GeminiClient

# --- Импорты Реализаций ---
from src.infrastructure.config import Settings, settings
from src.infrastructure.database.repositories.category_repository import (
    CategoryRepository,
)
from src.infrastructure.database.repositories.product_repository import (
    ProductRepository,
)
from src.infrastructure.database.repositories.user_repository import UserRepository
from src.infrastructure.database.uow import UnitOfWork
from src.infrastructure.memory.cart_repository import InMemoryCartRepository
from src.infrastructure.telegram.notifier import TelegramNotifier


class ConfigProvider(Provider):
    scope = Scope.APP

    @provide
    def get_config(self) -> Settings:
        return settings


class DbProvider(Provider):
    scope = Scope.APP

    @provide
    def get_engine(self, config: Settings) -> AsyncEngine:
        return create_async_engine(url=str(config.db.url))

    @provide
    def get_session_factory(
        self, engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session


class MemoryProvider(Provider):
    scope = Scope.APP

    @provide
    def get_cart_repo(self) -> ICartRepository:
        return InMemoryCartRepository()


class RepoProvider(Provider):
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

    @provide
    def get_uow(self, session: AsyncSession) -> IUnitOfWork:
        return UnitOfWork(session)


class AIProvider(Provider):
    scope = Scope.APP

    @provide
    def get_gemini_client(self, config: Settings) -> GeminiClient:
        return GeminiClient(settings=config)


class TelegramProvider(Provider):
    scope = Scope.APP

    @provide
    def get_bot(self, config: Settings) -> Bot:
        # поддержка aiogram 3.7+
        return Bot(
            token=config.bot.token.get_secret_value(),
            default=DefaultBotProperties(parse_mode="HTML"),
        )


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_notifier(self, bot: Bot) -> INotifier:
        return TelegramNotifier(bot)

    @provide
    def get_order_service(
        self, uow: IUnitOfWork, cart_repo: ICartRepository, notifier: INotifier
    ) -> OrderService:
        return OrderService(uow=uow, cart_repo=cart_repo, notifier=notifier)

    @provide
    def get_category_service(
        self, category_repo: ICategoryRepository
    ) -> CategoryService:
        return CategoryService(category_repo)

    @provide
    def get_product_service(
        self,
        product_repo: IProductRepository,
        category_repo: ICategoryRepository,
    ) -> ProductService:
        return ProductService(product_repo, category_repo)

    @provide
    def get_user_service(self, uow: IUnitOfWork) -> UserService:
        return UserService(uow)

    @provide
    def get_ai_consultant_service(
        self,
        gemini_client: GeminiClient,
        product_repo: IProductRepository,
    ) -> AIConsultantService:
        return AIConsultantService(gemini_client, product_repo)
