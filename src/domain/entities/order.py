from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum


class OrderStatus(Enum):
    """Статусы заказа."""
    PENDING = "pending"  # В ожидании
    PAID = "paid"        # Оплачен
    CANCELLED = "cancelled" # Отменен


@dataclass
class Order:
    """Доменная сущность 'Заказ'."""
    id: int
    user_id: int
    status: OrderStatus
    created_at: datetime
    total_amount: Decimal