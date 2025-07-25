from typing import AsyncGenerator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# --- Импорты Интерфейсов (Контрактов) ---
from src.application.contracts.cart.cart_repository import ICartRepository
from src.application.contracts.order.order_repository import (
    IOrderItemRepository,
    IOrderRepository,
)
from src.application.contracts.persistence.uow import IUnitOfWork
from src.application.interfaces.repositories.category_repository import (
    ICategoryRepository,
)
from src.application.interfaces.repositories.product_repository import (
    IProductRepository,
)
from src.application.interfaces.repositories.user_repository import IUserRepository

# --- Импорты Сервисов ---
from src.application.services.catalog import CategoryService, ProductService
from src.application.services.order_service import OrderService
from src.application.services.user_service import UserService

# --- Импорты Конфигурации и Реализаций ---
from src.infrastructure.config import Settings, settings
from src.infrastructure.database.repositories.category_repository import (
    CategoryRepository,
)
from src.infrastructure.database.repositories.order_repository import (
    OrderItemRepository,
    OrderRepository,
)
from src.infrastructure.database.repositories.product_repository import (
    ProductRepository,
)
from src.infrastructure.database.repositories.user_repository import UserRepository
from src.infrastructure.database.uow import UnitOfWork
from src.infrastructure.memory.cart_repository import InMemoryCartRepository


class ConfigProvider(Provider):
    scope = Scope.APP
    @provide
    def get_config(self) -> Settings:
        return settings

class DbProvider(Provider):
    scope = Scope.APP
    @provide
    def get_engine(self, config: Settings) -> AsyncEngine:
        return create_async_engine(url=config.db.url)

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
    @provide(scope=Scope.APP) # ЯВНО УКАЗЫВАЕМ СКОУП APP (SINGLETON)
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
    def get_order_repo(self, session: AsyncSession) -> IOrderRepository:
        return OrderRepository(session)

    @provide
    def get_order_item_repo(self, session: AsyncSession) -> IOrderItemRepository:
        return OrderItemRepository(session)
        
    @provide
    def get_uow(self, session: AsyncSession) -> IUnitOfWork:
        return UnitOfWork(session)

class ServiceProvider(Provider):
    scope = Scope.REQUEST

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
    def get_order_service(
        self,
        uow: IUnitOfWork,
        cart_repo: ICartRepository,
        # Удалены неиспользуемые зависимости order_repo и order_item_repo
    ) -> OrderService:
        # Передаем только те зависимости, которые реально нужны сервису
        return OrderService(uow, cart_repo)
    # --- КОНЕЦ ИСПРАВЛЕНИЯ ---

    # --- НАЧАЛО ИСПРАВЛЕНИЯ ---
    # Эта функция теперь имеет правильный отступ
    @provide
    def get_user_service(self, uow: IUnitOfWork) -> UserService:
        return UserService(uow)
    # --- КОНЕЦ ИСПРАВЛЕНИЯ ---