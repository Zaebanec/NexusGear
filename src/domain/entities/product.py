from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class Product:
    """
    Доменная сущность 'Товар'.

    Представляет товар, доступный для покупки в магазине.
    """
    id: int
    name: str
    description: str
    price: Decimal
    category_id: int
    created_at: datetime