import pytest
from aiohttp import web
from decimal import Decimal
import hmac, hashlib


@pytest.mark.asyncio
async def test_order_success_and_admin_status():
    from src.presentation.web.app import setup_app
    from dishka import make_async_container, Provider, Scope, provide
    # --- Bot stub ---
    class BotStub:
        async def set_webhook(self, *args, **kwargs):
            return None
        async def delete_webhook(self, *args, **kwargs):
            return None
        async def send_message(self, *args, **kwargs):
            return None

    bot_stub = BotStub()

    from aiogram import Bot as AiogramBot, Dispatcher

    class TestTelegramProvider(Provider):
        scope = Scope.APP
        @provide
        def get_bot(self) -> AiogramBot:  # type: ignore[override]
            return bot_stub

    # --- Fake repositories & UoW ---
    from contextlib import asynccontextmanager
    from typing import Optional, Iterable

    from src.application.contracts.persistence.uow import IUnitOfWork
    from src.application.contracts.order.order_repository import IOrderRepository, IOrderItemRepository
    from src.application.interfaces.repositories.user_repository import IUserRepository
    from src.application.interfaces.repositories.product_repository import IProductRepository
    from src.domain.entities.user import User as DomainUser
    from src.domain.entities.product import Product as DomainProduct
    from src.domain.entities.order import Order as DomainOrder, OrderStatus
    from src.domain.entities.order_item import OrderItem as DomainOrderItem

    class FakeUserRepo(IUserRepository):
        async def get_by_id(self, user_id: int) -> Optional[DomainUser]:
            return DomainUser(id=1, telegram_id=123, full_name="Test", username="test", created_at=None)  # type: ignore[arg-type]
        async def get_by_telegram_id(self, telegram_id: int) -> Optional[DomainUser]:
            if telegram_id == 123:
                return DomainUser(id=1, telegram_id=123, full_name="Test", username="test", created_at=None)  # type: ignore[arg-type]
            return None
        async def add(self, user: DomainUser) -> DomainUser:
            return user

    class FakeProductRepo(IProductRepository):
        async def get_by_id(self, product_id: int) -> Optional[DomainProduct]:
            if product_id == 10:
                return DomainProduct(id=10, name="P", description="D", price=Decimal("100.00"), category_id=1, created_at=None)  # type: ignore[arg-type]
            return None
        async def get_by_category_id(self, category_id: int) -> list[DomainProduct]:
            return []
        async def get_all(self) -> list[DomainProduct]:
            return []
        async def add(self, product: DomainProduct) -> DomainProduct:
            return product
        async def update(self, product: DomainProduct) -> Optional[DomainProduct]:
            return product
        async def delete(self, product_id: int) -> bool:
            return True

    class FakeOrderRepo(IOrderRepository):
        def __init__(self):
            self._orders: dict[int, DomainOrder] = {}
            self._seq = 1
        async def create(self, order: DomainOrder) -> DomainOrder:
            oid = self._seq
            self._seq += 1
            order.id = oid
            # store without items to avoid recursion on dataclasses.asdict
            order.items = []
            self._orders[oid] = order
            return order
        async def get_by_id(self, order_id: int) -> Optional[DomainOrder]:
            return self._orders.get(order_id)
        async def get_all(self) -> list[DomainOrder]:
            return list(self._orders.values())
        async def update_status(self, order_id: int, status: str) -> Optional[DomainOrder]:
            o = self._orders.get(order_id)
            if not o:
                return None
            o.status = OrderStatus(status)
            return o

    class FakeOrderItemRepo(IOrderItemRepository):
        def __init__(self):
            self._items: list[DomainOrderItem] = []
        async def create_items(self, items: Iterable[DomainOrderItem]) -> None:
            # store shallow copies without backref to avoid recursion in dataclasses.asdict later
            for it in items:
                self._items.append(DomainOrderItem(
                    id=it.id,
                    product_id=it.product_id,
                    quantity=it.quantity,
                    price_at_purchase=it.price_at_purchase,
                    order=DomainOrder(id=it.order.id, user_id=it.order.user_id, status=it.order.status, total_amount=it.order.total_amount, created_at=it.order.created_at, items=[]),
                ))
        async def get_by_order_id(self, order_id: int) -> list[DomainOrderItem]:
            return [i for i in self._items if i.order.id == order_id]

    # Shared repositories across requests to persist state between API calls
    shared_orders = FakeOrderRepo()
    shared_order_items = FakeOrderItemRepo()

    class FakeUoW(IUnitOfWork):
        def __init__(self):
            self.orders = shared_orders
            self.order_items = shared_order_items
            self.users = FakeUserRepo()
            self.products = FakeProductRepo()
        @asynccontextmanager
        async def atomic(self):
            yield

    # --- Services provider override ---
    from src.application.services.order_service import OrderService
    from src.application.contracts.notifications.notifier import INotifier

    class DummyNotifier(INotifier):
        async def notify_order_created(self, telegram_id: int, order: DomainOrder, *, full_name=None, phone=None, address=None) -> None:  # type: ignore[override]
            return None

    class TestServiceProvider(Provider):
        scope = Scope.REQUEST
        @provide
        def get_uow(self) -> IUnitOfWork:
            return FakeUoW()
        @provide
        def get_notifier(self) -> INotifier:
            return DummyNotifier()
        @provide
        def get_order_service(self, uow: IUnitOfWork, notifier: INotifier) -> OrderService:
            return OrderService(uow=uow, notifier=notifier)

    # Build container and app
    from src.infrastructure.di.providers import ConfigProvider, MemoryProvider
    container = make_async_container(
        ConfigProvider(),
        MemoryProvider(),
        TestTelegramProvider(),
        TestServiceProvider(),
    )
    dp = Dispatcher(dishka_container=container)
    app = setup_app(dishka_container=container, bot=bot_stub, dispatcher=dp)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="127.0.0.1", port=0)
    await site.start()
    sock = next(iter(site._server.sockets))
    host, port = sock.getsockname()[:2]
    base = f"http://{host}:{port}"

    import aiohttp
    async with aiohttp.ClientSession() as session:
        # create order successfully
        payload = {
            "items": [{"product_id": 10, "quantity": 2}],
            "user": {"id": 123},
            "full_name": "Test User",
            "phone": "+79990000000",
            "address": "Street 1",
        }
        r = await session.post(base + "/api/create_order", json=payload)
        data = await r.json()
        assert r.status == 200 and data.get("status") == "ok"
        order_id = int(data["order_id"])  # type: ignore[index]

        # patch status via admin API
        from src.infrastructure.config import settings
        secret = settings.app.secret_token.get_secret_value()
        admin_user = "123"
        token = hmac.new(secret.encode(), admin_user.encode(), hashlib.sha256).hexdigest()
        r2 = await session.patch(
            base + f"/api/v1/admin/orders/{order_id}",
            json={"status": "paid"},
            headers={"X-Admin-Token": token, "X-Admin-User": admin_user},
        )
        assert r2.status == 200
        data2 = await r2.json()
        assert data2.get("status") == "paid"

    await runner.cleanup()


