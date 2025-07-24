# src/application/services/order_service.py

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

    async def create_order_from_cart(self, internal_user_id: int, telegram_id: int) -> Order:
        # --- НАЧАЛО ИЗМЕНЕНИЯ: УДАЛЕНА ВНЕШНЯЯ ТРАНЗАКЦИЯ ---
        # async with self.uow.atomic(): <-- ЭТА СТРОКА УДАЛЕНА

        # Используем telegram_id для получения корзины
        cart_items = await self.cart_repo.get_by_user_id(telegram_id)
        if not cart_items:
            raise ValueError("Корзина пуста. Невозможно создать заказ.")

        total_amount = sum(item.price * item.quantity for item in cart_items)

        # Используем internal_user_id для создания заказа в БД
        order_entity = Order(
            id=0, user_id=internal_user_id, status=OrderStatus.PENDING,
            total_amount=total_amount, created_at=None
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

        # Используем telegram_id для очистки корзины
        await self.cart_repo.clear_by_user_id(telegram_id)

        # Коммит произойдет на уровне хендлера
        return created_order
        # --- КОНЕЦ ИЗМЕНЕНИЯ ---