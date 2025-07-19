from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.contracts.persistence.uow import IUnitOfWork

class UnitOfWork(IUnitOfWork):
    """
    Реализация паттерна Unit of Work для управления транзакциями SQLAlchemy.
    """
    def __init__(self, session: AsyncSession):
        self._session = session

    @asynccontextmanager
    async def atomic(self):
        """
        Обеспечивает атомарное выполнение операций.
        Использует встроенный механизм `begin()` сессии, который автоматически
        выполняет commit при успешном выходе из блока `async with`
        или rollback при любом исключении.
        """
        async with self._session.begin():
            yield