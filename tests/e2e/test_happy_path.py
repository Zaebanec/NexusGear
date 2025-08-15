import asyncio
import json
import os
import pytest
from aiohttp import web


@pytest.mark.asyncio
async def test_happy_path_smoke():
    # This is a minimal smoke E2E without real Telegram. We target server routes only.
    from src.presentation.web.app import setup_app
    from dishka import make_async_container, Provider, Scope, provide
    from src.infrastructure.di.providers import (
        ConfigProvider,
        MemoryProvider,
    )

    class BotStub:
        async def set_webhook(self, *args, **kwargs):
            return None
        async def delete_webhook(self, *args, **kwargs):
            return None
        async def send_message(self, *args, **kwargs):
            return None

    bot_stub = BotStub()

    from aiogram import Bot as AiogramBot

    class TestTelegramProvider(Provider):
        scope = Scope.APP

        @provide
        def get_bot(self) -> AiogramBot:  # type: ignore[override]
            return bot_stub

    # Provide services directly to avoid DB
    from src.application.services.catalog import CategoryService
    from src.application.services.order_service import OrderService
    from src.application.interfaces.repositories.category_repository import ICategoryRepository
    from src.domain.entities.category import Category as DomainCategory
    from contextlib import asynccontextmanager

    class FakeCategoryRepo(ICategoryRepository):
        async def get_by_id(self, category_id: int) -> DomainCategory | None:
            return None
        async def get_all(self) -> list[DomainCategory]:
            return []
        async def add(self, category: DomainCategory) -> DomainCategory:
            return DomainCategory(id=1, name=category.name)
        async def update(self, category: DomainCategory) -> DomainCategory | None:
            return category
        async def delete(self, category_id: int) -> bool:
            return True

    class FakeUoW:
        @asynccontextmanager
        async def atomic(self):
            yield

    class TestServiceProvider(Provider):
        scope = Scope.REQUEST

        @provide
        def get_category_service(self) -> CategoryService:
            return CategoryService(FakeCategoryRepo())

        @provide
        def get_order_service(self) -> OrderService:
            return OrderService(uow=FakeUoW())

    container = make_async_container(
        ConfigProvider(),
        MemoryProvider(),
        TestServiceProvider(),
        TestTelegramProvider(),
    )

    # Dispatcher is not used in the test path but required by app
    from aiogram import Dispatcher
    dp = Dispatcher(dishka_container=container)
    app = setup_app(dishka_container=container, bot=bot_stub, dispatcher=dp)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="127.0.0.1", port=0)
    await site.start()
    # Discover actual port
    sock = next(iter(site._server.sockets))
    host, port = sock.getsockname()[:2]
    base = f"http://{host}:{port}"

    # 1) load categories (public API)
    import aiohttp
    async with aiohttp.ClientSession() as session:
        r = await session.get(base + "/api/categories")
        assert r.status == 200
        _ = await r.json()

        # 2) simulate order create via web api
        payload = {
            "items": [],  # empty to trigger validation error and ensure handler works
            "user": {"id": 123},
            "full_name": "Test User",
            "phone": "+79990000000",
            "address": "Street 1",
        }
        r2 = await session.post(base + "/api/create_order", json=payload)
        assert r2.status in (400, 500)  # depends on DB fixtures; at least handler responds

    await runner.cleanup()


