# /var/www/nexus-gear-store/src/presentation/web/app.py - ФИНАЛЬНАЯ ВЕРСИЯ

from aiohttp import web
import aiohttp_cors
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from dishka import AsyncContainer, Scope
import logging

from src.infrastructure.config import settings
from src.application.contracts.persistence.uow import IUnitOfWork
from src.application.services.order_service import OrderService
from .api.handlers.category import get_categories
from .api.handlers.product import get_products_by_category
from .api_handlers import routes as api_routes
from .api.schemas.order import CreateOrderSchema
from pydantic import ValidationError
from .middlewares import admin_rate_limit_middleware
from .errors import json_error
from .app_keys import APP_DISHKA_CONTAINER, APP_BOT, APP_DISPATCHER

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{settings.app.base_url}{WEBHOOK_PATH}"

async def on_startup(app: web.Application):
    bot: Bot = app[APP_BOT]
    await bot.set_webhook(
        url=WEBHOOK_URL,
        secret_token=settings.app.secret_token.get_secret_value(),
        drop_pending_updates=True
    )
    logging.info(f"Webhook установлен на: {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    bot: Bot = app[APP_BOT]
    await bot.delete_webhook()
    logging.info("Webhook удален.")

async def webhook_handler(request: web.Request) -> web.Response:
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if secret != settings.app.secret_token.get_secret_value():
        logging.warning("Received an update with invalid secret token!")
        return web.Response(status=403)

    bot: Bot = request.app[APP_BOT]
    dispatcher: Dispatcher = request.app[APP_DISPATCHER]
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dispatcher.feed_update(bot=bot, update=update)
    return web.Response()

async def create_order_api_handler(request: web.Request) -> web.Response:
    try:
        data = await request.json()
        logging.info(f"--- Received data for order creation: {data} ---")

        try:
            order_data = CreateOrderSchema.model_validate(data)
        except ValidationError as e:
            logging.error(f"TWA data validation error: {e}")
            return json_error(
                "Bad request",
                code="bad_request",
                status=400,
                details={"errors": e.errors()},
            )

        telegram_id = order_data.user.id
        dishka_container: AsyncContainer = request.app[APP_DISHKA_CONTAINER]

        async with dishka_container(scope=Scope.REQUEST) as request_container:
            uow = await request_container.get(IUnitOfWork)
            order_service = await request_container.get(OrderService)

            async with uow.atomic():
                order = await order_service.create_order_from_api(
                    telegram_id=telegram_id,
                    items=[item.model_dump() for item in order_data.items],
                    full_name=order_data.full_name,
                    phone=order_data.phone,
                    address=order_data.address,
                )

        # раньше здесь было bot.send_message(...).
        # Теперь уведомление отправляет сам сервис через INotifier.

        return web.json_response({"status": "ok", "order_id": order.id})

    except ValueError as e:
        logging.error(f"Order creation bad request: {e}")
        return json_error("Bad request", code="bad_request", status=400, details={"message": str(e)})
    except Exception as e:
        logging.error(f"Critical error in create_order_api_handler: {e}", exc_info=True)
        return json_error("Internal server error", code="internal_error", status=500)

def setup_app(
    dishka_container: AsyncContainer, bot: Bot, dispatcher: Dispatcher
) -> web.Application:
    app = web.Application(middlewares=[admin_rate_limit_middleware()])
    app[APP_DISHKA_CONTAINER] = dishka_container
    app[APP_BOT] = bot
    app[APP_DISPATCHER] = dispatcher

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*",
        )
    })

    # Регистрируем все роуты
    app.router.add_static("/assets", path="src/presentation/web/static/assets", name="assets")

    async def index_handler(request: web.Request) -> web.StreamResponse:
        return web.FileResponse("src/presentation/web/static/index.html")

    app.router.add_get("/", index_handler)

    app.router.add_post(WEBHOOK_PATH, webhook_handler)
    app.router.add_get("/api/categories", get_categories)
    app.router.add_post("/api/create_order", create_order_api_handler)
    app.router.add_get("/api/products", get_products_by_category)
    app.add_routes(api_routes)

    # SPA fallback: любые не-API запросы отдаем index.html, чтобы роутер фронта работал по прямым ссылкам
    app.router.add_get("/{tail:.*}", index_handler)

    # Применяем CORS ко всем зарегистрированным роутам
    for route in list(app.router.routes()):
        cors.add(route)

    return app