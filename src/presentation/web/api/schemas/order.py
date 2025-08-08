# src/presentation/web/api/schemas/order.py

from pydantic import BaseModel, Field
from typing import List, Optional

class OrderItemSchema(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)

class UserSchema(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None

class CreateOrderSchema(BaseModel):
    items: List[OrderItemSchema]
    user: UserSchema
    # Добавляем поля из формы TWA
    full_name: str
    phone: str
    address: str