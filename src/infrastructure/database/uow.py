# src/infrastructure/database/uow.py - ПОЛНАЯ ВЕРСИЯ

from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.contracts.order.order_repository import IOrderRepository
from src.application.interfaces.repositories.user_repository import IUserRepository
from src.application.contracts.persistence.uow import IUnitOfWork

from src.infrastructure.database.repositories.order_repository import OrderRepository
from src.infrastructure.database.repositories.user_repository import UserRepository


class UnitOfWork(IUnitOfWork):
    def __init__(self, session: AsyncSession):
        self._session = session
        
        self.orders: IOrderRepository = OrderRepository(self._session)
        # --- ИЗМЕНЕНИЕ: Добавляем недостающий репозиторий пользователей ---
        self.users: IUserRepository = UserRepository(self._session)

    @asynccontextmanager
    async def atomic(self):
        async with self._session.begin():
            yield