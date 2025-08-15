from abc import ABC, abstractmethod
from typing import AsyncIterator, AsyncContextManager

from src.application.contracts.order.order_repository import (
    IOrderItemRepository,
    IOrderRepository,
)
from src.application.interfaces.repositories.product_repository import (
    IProductRepository,
)
from src.application.interfaces.repositories.user_repository import (
    IUserRepository,
)

class IUnitOfWork(ABC):
    orders: IOrderRepository
    order_items: IOrderItemRepository
    users: IUserRepository
    products: IProductRepository

    @abstractmethod
    def atomic(self) -> AsyncContextManager[None]:
        raise NotImplementedError