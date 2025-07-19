from decimal import Decimal
from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int]
    price_at_purchase: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    # Отношение обратно к заказу
    order: Mapped["Order"] = relationship(back_populates="items")