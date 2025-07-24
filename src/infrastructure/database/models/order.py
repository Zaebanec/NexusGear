from datetime import datetime
from decimal import Decimal
# --- НАЧАЛО ИЗМЕНЕНИЙ ---
from sqlalchemy import BigInteger, Enum as SAEnum, ForeignKey, Numeric, func
# --- КОНЕЦ ИЗМЕНЕНИЙ ---
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.entities.order import OrderStatus
from .base import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    # --- НАЧАЛО ИЗМЕНЕНИЙ ---
    # Меняем тип на BigInteger, чтобы вместить большие Telegram User ID
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    # --- КОНЕЦ ИЗМЕНЕНИЙ ---
    status: Mapped[OrderStatus] = mapped_column(SAEnum(OrderStatus), default=OrderStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    items: Mapped[list["OrderItem"]] = relationship(back_populates="order")