import pytest
from aiohttp import web


@pytest.mark.asyncio
async def test_admin_products_filter_by_category():
    # Setup app
    from src.presentation.web.app import setup_app
    from dishka import make_async_container, Provider, Scope, provide
    from src.infrastructure.di.providers import ConfigProvider, MemoryProvider
    from aiogram import Dispatcher

    # Provide ProductService for request scope similar to other e2e tests
    from src.application.services.catalog import ProductService, CategoryService
    from src.application.interfaces.repositories.product_repository import IProductRepository
    from src.application.interfaces.repositories.category_repository import ICategoryRepository
    from src.domain.entities.category import Category as DomainCategory
    from src.domain.entities.product import Product as DomainProduct

    class TestServiceProvider(Provider):
        scope = Scope.REQUEST
        @provide
        def get_category_service(self) -> CategoryService:
            class DummyCatRepo(ICategoryRepository):
                async def get_by_id(self, category_id: int):
                    return DomainCategory(id=category_id, name=f"C{category_id}")
                async def get_all(self):
                    return [DomainCategory(id=1, name="C1"), DomainCategory(id=2, name="C2")]
                async def add(self, category: DomainCategory):
                    return category
                async def update(self, category: DomainCategory):
                    return category
                async def delete(self, category_id: int):
                    return True
            return CategoryService(DummyCatRepo())
        @provide
        def get_product_service(self) -> ProductService:
            class DummyProdRepo(IProductRepository):
                async def get_by_id(self, product_id: int):
                    return DomainProduct(id=product_id, name="P", description="D", price=1, category_id=1, created_at=None)  # type: ignore[arg-type]
                async def get_by_category_id(self, category_id: int):
                    return []
                async def get_all(self):
                    return []
                async def add(self, product: DomainProduct):
                    return product
                async def update(self, product: DomainProduct):
                    return product
                async def delete(self, product_id: int):
                    return True
            # CategoryService with dummy repo
            return ProductService(DummyProdRepo(), CategoryService.__annotations__.get('category_repo') if False else CategoryService(type('X',(object,),{'get_by_id':lambda *_:DomainCategory(id=1,name='C1')})()))

    # use only in-memory/fake services to avoid real DB connections
    container = make_async_container(ConfigProvider(), MemoryProvider(), TestServiceProvider())
    dp = Dispatcher(dishka_container=container)

    class BotStub:
        async def set_webhook(self, *a, **k):
            return None
        async def delete_webhook(self, *a, **k):
            return None

    app = setup_app(dishka_container=container, bot=BotStub(), dispatcher=dp)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="127.0.0.1", port=0)
    await site.start()
    sock = next(iter(site._server.sockets))
    host, port = sock.getsockname()[:2]
    base = f"http://{host}:{port}"

    from src.infrastructure.config import settings
    import hmac, hashlib
    secret = settings.app.secret_token.get_secret_value()
    admin_user = "123"
    token = hmac.new(secret.encode(), admin_user.encode(), hashlib.sha256).hexdigest()
    headers = {"X-Admin-Token": token, "X-Admin-User": admin_user}

    import aiohttp
    async with aiohttp.ClientSession() as session:
        # Without category filter
        r1 = await session.get(base + "/api/v1/admin/products?limit=10&offset=0", headers=headers)
        assert r1.status in (200, 204)
        # With category filter
        r2 = await session.get(base + "/api/v1/admin/products?category_id=1&limit=10&offset=0", headers=headers)
        assert r2.status in (200, 204)

    await runner.cleanup()


@pytest.mark.asyncio
async def test_admin_orders_filters_status_and_dates():
    from src.presentation.web.app import setup_app
    from dishka import make_async_container, Provider, Scope, provide
    from src.infrastructure.di.providers import ConfigProvider, MemoryProvider
    from aiogram import Dispatcher

    # Provide OrderService for request scope similar to other e2e tests
    from src.application.services.order_service import OrderService
    from src.application.contracts.notifications.notifier import INotifier
    from src.application.contracts.persistence.uow import IUnitOfWork
    from contextlib import asynccontextmanager
    from src.domain.entities.order import Order as DomainOrder, OrderStatus

    class DummyNotifier(INotifier):
        async def notify_order_created(self, telegram_id: int, order, *, full_name=None, phone=None, address=None):
            return None

    class TestServiceProvider(Provider):
        scope = Scope.REQUEST
        @provide
        def get_notifier(self) -> INotifier:
            return DummyNotifier()
        @provide
        def get_order_service(self, notifier: INotifier) -> OrderService:
            class DummyUoW(IUnitOfWork):
                def __init__(self):
                    class O:
                        async def get_all(self):
                            return []
                    class OI:
                        async def get_by_order_id(self, oid:int):
                            return []
                    self.orders = O()
                    self.order_items = OI()
                @asynccontextmanager
                async def atomic(self):
                    yield
            return OrderService(uow=DummyUoW(), notifier=notifier)

    container = make_async_container(ConfigProvider(), MemoryProvider(), TestServiceProvider())
    dp = Dispatcher(dishka_container=container)

    class BotStub:
        async def set_webhook(self, *a, **k):
            return None
        async def delete_webhook(self, *a, **k):
            return None

    app = setup_app(dishka_container=container, bot=BotStub(), dispatcher=dp)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="127.0.0.1", port=0)
    await site.start()
    sock = next(iter(site._server.sockets))
    host, port = sock.getsockname()[:2]
    base = f"http://{host}:{port}"

    from src.infrastructure.config import settings
    import hmac, hashlib
    secret = settings.app.secret_token.get_secret_value()
    admin_user = "123"
    token = hmac.new(secret.encode(), admin_user.encode(), hashlib.sha256).hexdigest()
    headers = {"X-Admin-Token": token, "X-Admin-User": admin_user}

    import aiohttp
    async with aiohttp.ClientSession() as session:
        r = await session.get(base + "/api/v1/admin/orders?status=paid&created_from=2025-01-01T00:00:00&created_to=2025-12-31T23:59:59&limit=10&offset=0", headers=headers)
        assert r.status in (200, 204)

    await runner.cleanup()


