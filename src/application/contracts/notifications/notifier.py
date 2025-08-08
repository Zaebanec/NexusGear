# src/application/contracts/notifications/notifier.py
from __future__ import annotations
from typing import Protocol, Optional
from src.domain.entities.order import Order

class INotifier(Protocol):
    async def notify_order_created(
        self,
        telegram_id: int,
        order: Order,
        full_name: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
    ) -> None: ...
