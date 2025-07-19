from abc import ABC, abstractmethod
from src.domain.entities.order import Order
from src.domain.entities.order_item import OrderItem

class IOrderRepository(ABC):
    @abstractmethod
    async def create(self, order: Order) -> Order:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, order_id: int) -> Order | None:
        raise NotImplementedError

class IOrderItemRepository(ABC):
    @abstractmethod
    async def create_items(self, items: list[OrderItem]) -> None:
        raise NotImplementedError