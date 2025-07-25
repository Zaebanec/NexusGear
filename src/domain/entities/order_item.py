# src/domain/entities/order_item.py

from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING

# Используем TYPE_CHECKING для избежания циклического импорта во время выполнения
if TYPE_CHECKING:
    from .order import Order


@dataclass
class OrderItem:
    """Доменная сущность 'Позиция в заказе'."""
    id: int
    product_id: int
    quantity: int
    price_at_purchase: Decimal

    # --- КЛЮЧЕВЫЕ ИЗМЕНЕНИЯ ---
    # 1. Добавляем поле для хранения объекта Order.
    #    Используем строковый тип "Order" (forward reference) для избежания
    #    циклического импорта с order.py.
    #    repr=False, чтобы избежать бесконечной рекурсии при отладке.
    order: "Order" = field(repr=False)

    # 2. Поле order_id теперь опционально и вычисляемо.
    #    init=False означает, что его не нужно передавать в конструктор.
    order_id: int = field(init=False)

    # 3. __post_init__ - это специальный метод dataclass, который вызывается
    #    сразу после __init__. Мы используем его, чтобы синхронизировать
    #    order_id из переданного объекта order.
    def __post_init__(self):
        self.order_id = self.order.id