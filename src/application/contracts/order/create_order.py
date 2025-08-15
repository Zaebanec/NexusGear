# src/application/contracts/order/create_order.py

from typing import Annotated
from pydantic import BaseModel, Field

class OrderItemIn(BaseModel):
    product_id: Annotated[int, Field(strict=True, gt=0)]
    quantity: Annotated[int, Field(strict=True, gt=0)]

class CreateOrderIn(BaseModel):
    telegram_id: int
    items: list[OrderItemIn]

class CreateOrderOut(BaseModel):
    order_id: int
    status: str = "ok"
