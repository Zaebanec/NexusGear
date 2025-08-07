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
        logging.info(f"--- Received data from TWA: {data} ---")

        user_data = data.get("user")

        if not user_data or not user_data.get("id"):
            logging.error("User data or user ID is missing in TWA initData.")
            return web.json_response(
                {"status": "error", "message": "Не удалось идентифицировать пользователя. Попробуйте перезапустить бота."},
                status=400
            )
        
        # --- НАЧАЛО ИСПРАВЛЕНИЯ: Отступы исправлены ---
        telegram_id = int(user_data["id"])

        dishka_container: AsyncContainer = request.app["dishka_container"]
        
        async with dishka_container(scope=Scope.REQUEST) as request_container:
            uow = await request_container.get(IUnitOfWork)
            order_service = await request_container.get(OrderService)
            
            async with uow.atomic():
                order = await order_service.create_order(telegram_id=telegram_id)

        await bot.send_message(
            chat_id=telegram_id,
            text=(
                f"✅ Ваш заказ №{order.id} успешно создан!\n\n"
                f"<b>Получатель:</b> {data.get('full_name')}\n"
                f"<b>Телефон:</b> {data.get('phone')}\n"
                f"<b>Адрес:</b> {data.get('address')}\n\n"
                "В ближайшее время с вами свяжется наш менеджер."
            )
        )
        # --- КОНЕЦ ИСПРАВЛЕНИЯ ---

        return web.json_response({"status": "ok", "order_id": order.id})

    except Exception as e:
        logging.error(f"Critical error in create_order_api_handler: {e}", exc_info=True)
        return web.json_response({"status": "error", "message": "Внутренняя ошибка сервера. Пожалуйста, попробуйте позже."}, status=500)

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

    app.router.add_static("/static/", path="src/presentation/web/static", name="static")
    app.router.add_get("/", lambda req: web.FileResponse("src/presentation/web/static/admin.html"))
    app.router.add_get("/order", lambda req: web.FileResponse("src/presentation/web/static/order_form.html"))
    
    webhook_route = cors.add(app.router.add_resource(WEBHOOK_PATH))
    cors.add(webhook_route.add_route("POST", webhook_handler))

    order_api_route = cors.add(app.router.add_resource("/api/create_order"))
    cors.add(order_api_route.add_route("POST", create_order_api_handler))

    return app