# src/infrastructure/database/repositories/order_repository.py

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.contracts.order.order_repository import (
    IOrderItemRepository,
    IOrderRepository,
)
from src.domain.entities.order import Order as DomainOrder
from src.domain.entities.order_item import OrderItem as DomainOrderItem
from src.infrastructure.database.models import Order as DbOrder
from src.infrastructure.database.models import OrderItem as DbOrderItem

def _to_domain_order(db: DbOrder) -> DomainOrder:
    # Простейший маппер без загрузки items (при необходимости — дополним)
    return DomainOrder(
        id=db.id,
        user_id=db.user_id,
        status=db.status,
        total_amount=db.total_amount,
    )

class OrderRepository(IOrderRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, order: DomainOrder) -> DomainOrder:
        db_order = DbOrder(
            user_id=order.user_id,
            status=order.status,
            total_amount=order.total_amount,
        )
        self.session.add(db_order)
        await self.session.flush([db_order])
        order.id = db_order.id
        return order

    async def get_by_id(self, order_id: int) -> DomainOrder | None:
        stmt = select(DbOrder).where(DbOrder.id == order_id)
        db_order = await self.session.scalar(stmt)
        return _to_domain_order(db_order) if db_order else None

class OrderItemRepository(IOrderItemRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_items(self, items: list[DomainOrderItem]) -> None:
        db_items = [
            DbOrderItem(
                order_id=i.order_id,
                product_id=i.product_id,
                quantity=i.quantity,
                price_at_purchase=i.price_at_purchase,
            )
            for i in items
        ]
        self.session.add_all(db_items)
        # flush не обязателен здесь, транзакция закроется в UoW.atomic()
