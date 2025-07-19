from dataclasses import dataclass
from decimal import Decimal

@dataclass
class CartItem:
    """Представляет товар в корзине пользователя."""
    product_id: int
    name: str
    price: Decimal
    quantity: int