from dataclasses import dataclass
from decimal import Decimal


@dataclass
class OrderItem:
    """Доменная сущность 'Позиция в заказе'."""
    id: int
    order_id: int
    product_id: int
    quantity: int
    price_at_purchase: Decimal