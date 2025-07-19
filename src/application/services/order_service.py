from decimal import Decimal

from src.application.contracts.cart.cart_repository import ICartRepository
from src.application.contracts.order.order_repository import (
    IOrderItemRepository,
    IOrderRepository,
)
from src.application.contracts.persistence.uow import IUnitOfWork
from src.domain.entities.order import Order, OrderStatus
from src.domain.entities.order_item import OrderItem

class OrderService:
    def __init__(
        self,
        uow: IUnitOfWork,
        cart_repo: ICartRepository,
        order_repo: IOrderRepository,
        order_item_repo: IOrderItemRepository,
    ):
        self.uow = uow
        self.cart_repo = cart_repo
        self.order_repo = order_repo
        self.order_item_repo = order_item_repo

    async def create_order_from_cart(self, user_id: int) -> Order:
        async with self.uow.atomic():
            cart_items = await self.cart_repo.get_by_user_id(user_id)
            if not cart_items:
                raise ValueError("Корзина пуста. Невозможно создать заказ.")

            total_amount = sum(item.price * item.quantity for item in cart_items)

            # Создаем заказ
            order_entity = Order(
                id=0, user_id=user_id, status=OrderStatus.PENDING,
                total_amount=total_amount, created_at=None # Будет установлено БД
            )
            created_order = await self.order_repo.create(order_entity)

            # Создаем позиции заказа
            order_items = [
                OrderItem(
                    id=0, order_id=created_order.id, product_id=item.product_id,
                    quantity=item.quantity, price_at_purchase=item.price
                ) for item in cart_items
            ]
            await self.order_item_repo.create_items(order_items)

            # Очищаем корзину
            await self.cart_repo.clear_by_user_id(user_id)

            # Коммит транзакции произойдет автоматически при выходе из `uow.atomic()`

            return created_order