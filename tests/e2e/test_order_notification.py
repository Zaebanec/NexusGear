import asyncio
import json
import pytest
from aiohttp import web


@pytest.mark.asyncio
async def test_order_triggers_notification(monkeypatch):
    # Arrange app with dummy notifier recording calls
    from src.presentation.web.app import setup_app
    from dishka import make_async_container, Provider, Scope, provide

    calls = []

    class BotStub:
        async def set_webhook(self, *args, **kwargs):
            return None
        async def delete_webhook(self, *args, **kwargs):
            return None
        async def send_message(self, *args, **kwargs):
            calls.append((args, kwargs))
            return None

    bot_stub = BotStub()

    from aiogram import Bot as AiogramBot, Dispatcher

    class TestTelegramProvider(Provider):
        scope = Scope.APP
        @provide
        def get_bot(self) -> AiogramBot:  # type: ignore[override]
            return bot_stub

    # Fake UoW with minimal behavior for order creation
    from contextlib import asynccontextmanager
    from decimal import Decimal
    from typing import Optional
    from src.application.contracts.persistence.uow import IUnitOfWork
    from src.application.interfaces.repositories.user_repository import IUserRepository
    from src.application.interfaces.repositories.product_repository import IProductRepository
    from src.application.contracts.order.order_repository import IOrderRepository, IOrderItemRepository
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
        async def get_by_category_id(self, category_id: int):
            return []
        async def get_all(self):
            return []
        async def add(self, product: DomainProduct) -> DomainProduct:
            return product
        async def update(self, product: DomainProduct):
            return product
        async def delete(self, product_id: int) -> bool:
            return True

    class FakeOrderRepo(IOrderRepository):
        def __init__(self):
            self._seq = 1
        async def create(self, order: DomainOrder) -> DomainOrder:
            order.id = self._seq
            self._seq += 1
            order.items = []
            return order
        async def get_by_id(self, order_id: int):
            return None
        async def get_all(self):
            return []
        async def update_status(self, order_id: int, status: str):
            return None

    class FakeOrderItemRepo(IOrderItemRepository):
        async def create_items(self, items):
            return None
        async def get_by_order_id(self, order_id: int):
            return []

    class FakeUoW(IUnitOfWork):
        def __init__(self):
            self.users = FakeUserRepo()
            self.products = FakeProductRepo()
            self.orders = FakeOrderRepo()
            self.order_items = FakeOrderItemRepo()
        @asynccontextmanager
        async def atomic(self):
            yield

    from src.application.services.order_service import OrderService
    from src.application.contracts.notifications.notifier import INotifier

    class DummyNotifier(INotifier):
        async def notify_order_created(self, telegram_id: int, order: DomainOrder, *, full_name=None, phone=None, address=None) -> None:  # type: ignore[override]
            calls.append(((telegram_id, order.id), {"full_name": full_name}))

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

    from src.infrastructure.di.providers import ConfigProvider, MemoryProvider
    container = make_async_container(ConfigProvider(), MemoryProvider(), TestTelegramProvider(), TestServiceProvider())
    dp = Dispatcher(dishka_container=container)
    app = setup_app(dishka_container=container, bot=bot_stub, dispatcher=dp)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="127.0.0.1", port=0)
    await site.start()
    sock = next(iter(site._server.sockets))
    host, port = sock.getsockname()[:2]
    base = f"http://{host}:{port}"

    # Act: create order
    import aiohttp
    async with aiohttp.ClientSession() as session:
        payload = {
            "items": [{"product_id": 10, "quantity": 1}],
            "user": {"id": 123},
            "full_name": "Tester",
            "phone": "+79990000000",
            "address": "Street 1",
        }
        r = await session.post(base + "/api/create_order", json=payload)
        data = await r.json()
        assert r.status == 200 and data.get("status") == "ok"

    # Assert notifier was called at least once
    assert any(True for c in calls)


