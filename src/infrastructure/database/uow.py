# src/infrastructure/database/uow.py - ОБНОВЛЁННО

from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.contracts.order.order_repository import IOrderRepository, IOrderItemRepository
from src.application.interfaces.repositories.user_repository import IUserRepository
from src.application.interfaces.repositories.product_repository import IProductRepository
from src.application.contracts.persistence.uow import IUnitOfWork

from src.infrastructure.database.repositories.order_repository import OrderRepository, OrderItemRepository
from src.infrastructure.database.repositories.user_repository import UserRepository
from src.infrastructure.database.repositories.product_repository import ProductRepository


class UnitOfWork(IUnitOfWork):
    def __init__(self, session: AsyncSession):
        self._session = session

        self.orders: IOrderRepository = OrderRepository(self._session)
        self.order_items: IOrderItemRepository = OrderItemRepository(self._session)  # NEW
        self.users: IUserRepository = UserRepository(self._session)
        self.products: IProductRepository = ProductRepository(self._session)        # NEW

    def atomic(self):
        return self._atomic()

    @asynccontextmanager
    async def _atomic(self):
        async with self._session.begin():
            yield
