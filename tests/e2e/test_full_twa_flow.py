import pytest
from aiohttp import web


@pytest.mark.asyncio
async def test_full_flow_start_twa_order_notification():
    from src.presentation.web.app import setup_app
    from dishka import make_async_container, Provider, Scope, provide

    # --- Bot stub that records outgoing messages ---
    sent_messages: list[tuple[tuple, dict]] = []

    class BotStub:
        def __init__(self):
            # aiogram middlewares expect bot.id to exist
            self.id = 1
        async def __call__(self, method, *args, **kwargs):
            # emulate aiogram Bot being awaitable with TelegramMethod
            return None
        async def set_webhook(self, *args, **kwargs):
            return None

        async def delete_webhook(self, *args, **kwargs):
            return None

        async def send_message(self, *args, **kwargs):
            sent_messages.append((args, kwargs))
            return None

    bot_stub = BotStub()

    from aiogram import Bot as AiogramBot, Dispatcher

    class TestTelegramProvider(Provider):
        scope = Scope.APP

        @provide
        def get_bot(self) -> AiogramBot:  # type: ignore[override]
            return bot_stub  # type: ignore[return-value]

    # --- Fake repos & UoW to avoid DB ---
    from contextlib import asynccontextmanager
    from typing import Optional, Iterable
    from decimal import Decimal

    from src.application.contracts.persistence.uow import IUnitOfWork
    from src.application.contracts.order.order_repository import (
        IOrderRepository,
        IOrderItemRepository,
    )
    from src.application.interfaces.repositories.user_repository import IUserRepository
    from src.application.interfaces.repositories.product_repository import (
        IProductRepository,
    )
    from src.domain.entities.user import User as DomainUser
    from src.domain.entities.product import Product as DomainProduct
    from src.domain.entities.order import Order as DomainOrder, OrderStatus
    from src.domain.entities.order_item import OrderItem as DomainOrderItem

    class FakeUserRepo(IUserRepository):
        def __init__(self):
            self._users_by_tg: dict[int, DomainUser] = {}

        async def get_by_id(self, user_id: int) -> Optional[DomainUser]:
            for u in self._users_by_tg.values():
                if u.id == user_id:
                    return u
            return None

        async def get_by_telegram_id(self, telegram_id: int) -> Optional[DomainUser]:
            return self._users_by_tg.get(telegram_id)

        async def add(self, user: DomainUser) -> DomainUser:
            # assign deterministic id=1 for tests
            user.id = 1
            self._users_by_tg[user.telegram_id] = user
            return user

    class FakeProductRepo(IProductRepository):
        async def get_by_id(self, product_id: int) -> Optional[DomainProduct]:
            if product_id == 10:
                return DomainProduct(
                    id=10,
                    name="P",
                    description="D",
                    price=Decimal("100.00"),
                    category_id=1,
                    created_at=None,  # type: ignore[arg-type]
                )
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
            self._orders: dict[int, DomainOrder] = {}

        async def create(self, order: DomainOrder) -> DomainOrder:
            order.id = self._seq
            self._seq += 1
            order.items = []
            self._orders[order.id] = order
            return order

        async def get_by_id(self, order_id: int):
            return self._orders.get(order_id)

        async def get_all(self):
            return list(self._orders.values())

        async def update_status(self, order_id: int, status: str):
            o = self._orders.get(order_id)
            if not o:
                return None
            o.status = OrderStatus(status)
            return o

    class FakeOrderItemRepo(IOrderItemRepository):
        def __init__(self):
            self._items: list[DomainOrderItem] = []

        async def create_items(self, items: Iterable[DomainOrderItem]) -> None:
            for it in items:
                self._items.append(
                    DomainOrderItem(
                        id=it.id,
                        product_id=it.product_id,
                        quantity=it.quantity,
                        price_at_purchase=it.price_at_purchase,
                        order=DomainOrder(
                            id=it.order.id,
                            user_id=it.order.user_id,
                            status=it.order.status,
                            total_amount=it.order.total_amount,
                            created_at=it.order.created_at,
                            items=[],
                        ),
                    )
                )

        async def get_by_order_id(self, order_id: int) -> list[DomainOrderItem]:
            return [i for i in self._items if i.order.id == order_id]

    # Shared repositories across requests to persist state between /start and API call
    shared_users = FakeUserRepo()
    shared_orders = FakeOrderRepo()
    shared_order_items = FakeOrderItemRepo()

    class FakeUoW(IUnitOfWork):
        def __init__(self):
            self.users = shared_users
            self.products = FakeProductRepo()
            self.orders = shared_orders
            self.order_items = shared_order_items

        @asynccontextmanager
        async def atomic(self):
            yield

    # --- Services override: inject notifier to capture calls ---
    from src.application.services.order_service import OrderService
    from src.application.services.user_service import UserService
    from src.application.contracts.notifications.notifier import INotifier

    notifications: list[tuple[tuple, dict]] = []

    class DummyNotifier(INotifier):
        async def notify_order_created(
            self,
            telegram_id: int,
            order: DomainOrder,
            *,
            full_name=None,
            phone=None,
            address=None,
        ) -> None:  # type: ignore[override]
            notifications.append(((telegram_id, order.id), {"full_name": full_name}))

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

        @provide
        def get_user_service(self, uow: IUnitOfWork) -> UserService:
            return UserService(uow)

    # Build app
    from src.infrastructure.di.providers import ConfigProvider, MemoryProvider
    container = make_async_container(
        ConfigProvider(),
        MemoryProvider(),
        TestTelegramProvider(),
        TestServiceProvider(),
    )
    dp = Dispatcher(dishka_container=container)
    # include /start handler
    from src.presentation.handlers.common import common_router
    dp.include_router(common_router)
    app = setup_app(dishka_container=container, bot=bot_stub, dispatcher=dp)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="127.0.0.1", port=0)
    await site.start()
    sock = next(iter(site._server.sockets))
    host, port = sock.getsockname()[:2]
    base = f"http://{host}:{port}"

    # Step 1: Simulate Telegram /start via webhook
    import aiohttp
    from src.infrastructure.config import settings

    update_payload = {
        "update_id": 1,
        "message": {
            "message_id": 1,
            "from": {"id": 123, "is_bot": False, "first_name": "Tester"},
            "chat": {"id": 123, "type": "private"},
            "date": 0,
            "text": "/start",
            "entities": [{"offset": 0, "length": 6, "type": "bot_command"}],
        },
    }

    async with aiohttp.ClientSession() as session:
        r0 = await session.post(
            base + "/webhook",
            json=update_payload,
            headers={
                "X-Telegram-Bot-Api-Secret-Token": settings.app.secret_token.get_secret_value()
            },
        )
        assert r0.status in (200, 204)

        # Step 2: Create order via Web API (TWA action)
        payload = {
            "items": [{"product_id": 10, "quantity": 1}],
            "user": {"id": 123},
            "full_name": "Tester",
            "phone": "+79990000000",
            "address": "Street 1",
        }
        r1 = await session.post(base + "/api/create_order", json=payload)
        data = await r1.json()
        assert r1.status == 200 and data.get("status") == "ok"

    # Assert: user registered via /start and notifier was called for order
    assert (await shared_users.get_by_telegram_id(123)) is not None
    assert any(True for _ in notifications)

    await runner.cleanup()


