# src/application/services/order_service.py - ФИНАЛ v2 (с уведомлением)

from decimal import Decimal
from typing import List, Dict, Optional

from src.application.contracts.cart.cart_repository import ICartRepository
from src.application.contracts.notifications.notifier import INotifier
from src.application.contracts.persistence.uow import IUnitOfWork
from src.domain.entities.order import Order, OrderStatus
from src.domain.entities.order_item import OrderItem


class OrderService:
    def __init__(
        self,
        uow: IUnitOfWork,
        cart_repo: Optional[ICartRepository] = None,
        notifier: Optional[INotifier] = None,
    ):
        self.uow = uow
        self.cart_repo = cart_repo
        self.notifier = notifier

    async def create_order(self, telegram_id: int) -> Order:
        """Создает заказ на основе содержимого корзины пользователя."""
        user = await self.uow.users.get_by_telegram_id(telegram_id)
        if not user:
            raise ValueError(f"Пользователь с telegram_id {telegram_id} не найден.")

        if not self.cart_repo:
            raise ValueError("Cart repository is not configured")

        cart_items = await self.cart_repo.get_by_user_id(telegram_id)
        if not cart_items:
            raise ValueError("Корзина пуста")

        total = sum(item.price * item.quantity for item in cart_items)

        order = Order(
            id=0,
            user_id=user.id,
            status=OrderStatus.PENDING,
            total_amount=total,
        )

        await self.uow.orders.create(order)
        await self.cart_repo.clear_by_user_id(telegram_id)

        return order

    async def create_order_from_api(
        self,
        telegram_id: int,
        items: List[Dict],
        *,
        full_name: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
    ) -> Order:
        """
        items: [{ "product_id": int, "quantity": int }, ...]
        """
        user = await self.uow.users.get_by_telegram_id(telegram_id)
        if not user:
            raise ValueError(f"Пользователь с telegram_id {telegram_id} не найден.")
        if not items:
            raise ValueError("Список товаров пуст.")

        domain_items: list[OrderItem] = []
        total = Decimal("0.00")

        for raw in items:
            product_id = int(raw["product_id"])
            qty = int(raw["quantity"])
            if qty <= 0:
                raise ValueError(f"Некорректное количество для product_id={product_id}")

            product = await self.uow.products.get_by_id(product_id)
            if not product:
                raise ValueError(f"Товар {product_id} не найден.")

            price = product.price
            total += price * qty

            domain_items.append(
                OrderItem(
                    id=0,
                    order=None,  # установим после создания заказа
                    product_id=product_id,
                    quantity=qty,
                    price_at_purchase=price,
                )
            )

        order = Order(
            id=0,
            user_id=user.id,
            status=OrderStatus.PENDING,
            total_amount=total,
        )

        # Сохранение в транзакции осуществляется снаружи (uow.atomic())
        order = await self.uow.orders.create(order)

        for it in domain_items:
            it.order = order
            it.__post_init__()  # синхронизируем order_id

        await self.uow.order_items.create_items(domain_items)
        order.items = domain_items

        # Важно: уведомление вне DB flush'ей — после успешного создания
        await self.notifier.notify_order_created(
            telegram_id=telegram_id,
            order=order,
            full_name=full_name,
            phone=phone,
            address=address,
        )

        return order
