import pytest
from aiohttp import web


@pytest.mark.asyncio
async def test_checkout_validation_errors():
    from src.presentation.web.app import setup_app
    from dishka import make_async_container
    from src.infrastructure.di.providers import ConfigProvider, MemoryProvider
    from aiogram import Dispatcher

    # Minimal container/app (order service will error due to invalid user/product)
    container = make_async_container(ConfigProvider(), MemoryProvider())
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

    import aiohttp
    async with aiohttp.ClientSession() as session:
        # invalid body shape
        r = await session.post(base + "/api/create_order", json={"items": [], "user": {}})
        assert r.status == 400
        data = await r.json()
        assert "error" in data

        # invalid user id type
        r2 = await session.post(base + "/api/create_order", json={
            "items": [{"product_id": 1, "quantity": 1}],
            "user": {"id": "abc"},
            "full_name": "",
            "phone": "",
            "address": "",
        })
        assert r2.status == 400
        data2 = await r2.json()
        assert data2["error"]["code"] == "bad_request"

    await runner.cleanup()


