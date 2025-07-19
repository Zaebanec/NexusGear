from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.contracts.order.order_repository import (
    IOrderItemRepository,
    IOrderRepository,
)
from src.domain.entities.order import Order as DomainOrder
from src.domain.entities.order_item import OrderItem as DomainOrderItem
from src.infrastructure.database.models import Order as DbOrder
from src.infrastructure.database.models import OrderItem as DbOrderItem

# ... (здесь должны быть мапперы, но для краткости опустим)

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
        order.id = db_order.id # Обновляем ID в доменной сущности
        return order

    async def get_by_id(self, order_id: int) -> DomainOrder | None:
        # ... реализация получения заказа ...
        return None

class OrderItemRepository(IOrderItemRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_items(self, items: list[DomainOrderItem]) -> None:
        db_items = [
            DbOrderItem(
                order_id=item.order_id,
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_purchase=item.price_at_purchase,
            )
            for item in items
        ]
        self.session.add_all(db_items)