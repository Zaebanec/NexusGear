# src/domain/entities/order.py

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

# Избегаем циклического импорта
if TYPE_CHECKING:
    from .order_item import OrderItem


class OrderStatus(Enum):
    """Статусы заказа."""
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"


@dataclass
class Order:
    """Доменная сущность 'Заказ'."""
    id: int
    user_id: int
    status: OrderStatus
    total_amount: Decimal
    created_at: datetime = field(default_factory=datetime.utcnow)

    # --- КЛЮЧЕВОЕ ИЗМЕНЕНИЕ: Добавляем коллекцию для связанных позиций ---
    # SQLAlchemy будет использовать это поле для заполнения связанных объектов
    # при загрузке заказа из БД, если настроен relationship.
    # default_factory=list гарантирует, что поле будет пустым списком,
    # а не общим изменяемым объектом для всех экземпляров Order.
    items: list[OrderItem] = field(default_factory=list, repr=False)