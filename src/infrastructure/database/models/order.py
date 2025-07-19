from datetime import datetime
from decimal import Decimal
from sqlalchemy import Enum as SAEnum, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.entities.order import OrderStatus
from .base import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[OrderStatus] = mapped_column(SAEnum(OrderStatus), default=OrderStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    # Отношение к позициям заказа
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order")