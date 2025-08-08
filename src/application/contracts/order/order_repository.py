# src/application/contracts/order/order_repository.py

from __future__ import annotations
from typing import Protocol, Iterable, Optional
from src.domain.entities.order import Order as DomainOrder
from src.domain.entities.order_item import OrderItem as DomainOrderItem

class IOrderRepository(Protocol):
    async def create(self, order: DomainOrder) -> DomainOrder: ...
    async def get_by_id(self, order_id: int) -> Optional[DomainOrder]: ...

class IOrderItemRepository(Protocol):
    async def create_items(self, items: Iterable[DomainOrderItem]) -> None: ...
