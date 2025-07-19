from abc import ABC, abstractmethod
from contextlib import asynccontextmanager

class IUnitOfWork(ABC):
    @abstractmethod
    @asynccontextmanager
    async def atomic(self):
        raise NotImplementedError