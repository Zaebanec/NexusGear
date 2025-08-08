# src/application/contracts/order/create_order.py

from pydantic import BaseModel, conint

class OrderItemIn(BaseModel):
    product_id: conint(strict=True, gt=0)
    quantity: conint(strict=True, gt=0)

class CreateOrderIn(BaseModel):
    telegram_id: int
    items: list[OrderItemIn]

class CreateOrderOut(BaseModel):
    order_id: int
    status: str = "ok"
