# src/infrastructure/database/repositories/order_repository.py

from typing import Iterable
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.contracts.order.order_repository import (
    IOrderItemRepository,
    IOrderRepository,
)
from src.domain.entities.order import Order as DomainOrder, OrderStatus
from src.domain.entities.order_item import OrderItem as DomainOrderItem
from src.infrastructure.database.models import Order as DbOrder
from src.infrastructure.database.models import OrderItem as DbOrderItem

def _to_domain_order(db: DbOrder) -> DomainOrder:
    # Простейший маппер без загрузки items (при необходимости — дополним)
    return DomainOrder(
        id=db.id,
        user_id=db.user_id,
        status=OrderStatus(db.status) if not isinstance(db.status, OrderStatus) else db.status,
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

    async def get_all(self) -> list[DomainOrder]:
        stmt = select(DbOrder).order_by(DbOrder.id.desc())
        res = await self.session.execute(stmt)
        return [_to_domain_order(row) for row in res.scalars().all()]

    async def update_status(self, order_id: int, status: str) -> DomainOrder | None:
        stmt = select(DbOrder).where(DbOrder.id == order_id)
        db_order = await self.session.scalar(stmt)
        if not db_order:
            return None
        db_order.status = OrderStatus(status) if not isinstance(status, OrderStatus) else status
        await self.session.flush([db_order])
        return _to_domain_order(db_order)

class OrderItemRepository(IOrderItemRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_items(self, items: Iterable[DomainOrderItem]) -> None:
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

    async def get_by_order_id(self, order_id: int) -> list[DomainOrderItem]:
        stmt = select(DbOrderItem).where(DbOrderItem.order_id == order_id)
        res = await self.session.execute(stmt)
        rows = res.scalars().all()
        items: list[DomainOrderItem] = []
        for i in rows:
            db_parent = await self.session.get(DbOrder, i.order_id)
            if not db_parent:
                continue
            items.append(
                DomainOrderItem(
                    id=i.id,
                    order=_to_domain_order(db_parent),
                    product_id=i.product_id,
                    quantity=i.quantity,
                    price_at_purchase=i.price_at_purchase,
                )
            )
        return items
