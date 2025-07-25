# src/application/services/order_service.py - ФИНАЛЬНАЯ ВЕРСИЯ

from decimal import Decimal

from src.application.contracts.cart.cart_repository import ICartRepository
from src.application.contracts.persistence.uow import IUnitOfWork
from src.domain.entities.order import Order, OrderStatus
from src.domain.entities.order_item import OrderItem

class OrderService:
    def __init__(self, uow: IUnitOfWork, cart_repo: ICartRepository):
        self.uow = uow
        self.cart_repo = cart_repo

    # --- ИЗМЕНЕНИЕ 1: Метод теперь принимает telegram_id, а не абстрактный user_id ---
    async def create_order(self, telegram_id: int) -> Order:
        # --- ИЗМЕНЕНИЕ 2: Сервис сам находит пользователя в рамках своей транзакции ---
        # Это делает сервис более надежным и самодостаточным.
        user = await self.uow.users.get_by_telegram_id(telegram_id)
        if not user:
            # Этот код никогда не должен выполниться, если /start работает,
            # но это хорошая защитная мера.
            raise ValueError(f"Попытка создать заказ для несуществующего пользователя: {telegram_id}")

        cart_items = await self.cart_repo.get_by_user_id(telegram_id)
        if not cart_items:
            raise ValueError("Корзина пуста. Невозможно создать заказ.")

        total_amount = sum(item.price * item.quantity for item in cart_items)

        # --- ИЗМЕНЕНИЕ 3: Мы используем user.id (внутренний PK), а не telegram_id ---
        order_entity = Order(
            id=0,
            user_id=user.id, # <--- КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ
            status=OrderStatus.PENDING,
            total_amount=total_amount,
        )

        order_entity.items = [
            OrderItem(
                id=0,
                order=order_entity,
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_purchase=item.price
            ) for item in cart_items
        ]
        
        await self.uow.orders.create(order_entity)
        
        await self.cart_repo.clear_by_user_id(telegram_id)

        return order_entity