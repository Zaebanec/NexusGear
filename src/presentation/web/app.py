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
from .api.schemas.order import CreateOrderSchema
from pydantic import ValidationError

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{settings.app.base_url}{WEBHOOK_PATH}"

async def on_startup(app: web.Application):
    bot: Bot = app["bot"]
    await bot.set_webhook(
        url=WEBHOOK_URL,
        secret_token=settings.app.secret_token.get_secret_value(),
        drop_pending_updates=True
    )
    logging.info(f"Webhook установлен на: {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    bot: Bot = app["bot"]
    await bot.delete_webhook()
    logging.info("Webhook удален.")

async def webhook_handler(request: web.Request) -> web.Response:
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if secret != settings.app.secret_token.get_secret_value():
        logging.warning("Received an update with invalid secret token!")
        return web.Response(status=403)

    bot: Bot = request.app["bot"]
    dispatcher: Dispatcher = request.app["dispatcher"]
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dispatcher.feed_update(bot=bot, update=update)
    return web.Response()

async def create_order_api_handler(request: web.Request) -> web.Response:
    bot: Bot = request.app["bot"]
    
    try:
        data = await request.json()
        logging.info(f"--- Received data for order creation: {data} ---")

        try:
            order_data = CreateOrderSchema.model_validate(data)
        except ValidationError as e:
            logging.error(f"TWA data validation error: {e}")
            return web.json_response({"status": "error", "message": "Некорректные данные заказа."}, status=400)

        telegram_id = order_data.user.id
        dishka_container: AsyncContainer = request.app["dishka_container"]
        
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

    except Exception as e:
        logging.error(f"Critical error in create_order_api_handler: {e}", exc_info=True)
        return web.json_response({"status": "error", "message": "Внутренняя ошибка сервера."}, status=500)

def setup_app(
    dishka_container: AsyncContainer, bot: Bot, dispatcher: Dispatcher
) -> web.Application:
    app = web.Application()
    app["dishka_container"] = dishka_container
    app["bot"] = bot
    app["dispatcher"] = dispatcher

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
    app.router.add_get("/", lambda req: web.FileResponse("src/presentation/web/static/index.html"))
    
    app.router.add_post(WEBHOOK_PATH, webhook_handler)
    app.router.add_get("/api/categories", get_categories)
    app.router.add_post("/api/create_order", create_order_api_handler)
    app.router.add_get("/api/products", get_products_by_category)

    # Применяем CORS ко всем зарегистрированным роутам
    for route in list(app.router.routes()):
        cors.add(route)

    return app