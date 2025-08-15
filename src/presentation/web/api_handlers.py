# src/presentation/web/api_handlers.py

import dataclasses
import logging
from http import HTTPStatus

from aiohttp import web
from dishka import Scope

from src.application.services.catalog import CategoryService, ProductService
from src.application.services.order_service import OrderService
from src.presentation.web.api.schemas.product import (
    ProductSchema,
    ProductCreateSchema,
    ProductUpdateSchema,
)
from src.infrastructure.config import settings
import hashlib, hmac
from src.presentation.web.api.schemas.order import OrderItemSchema
from src.presentation.web.api.schemas.category import (
    CategorySchema,
    CategoryCreateSchema,
    CategoryUpdateSchema,
)
def _is_admin(request: web.Request) -> bool:
    token = request.headers.get("X-Admin-Token")
    user_id = request.headers.get("X-Admin-User")
    if not token or not user_id:
        return False
    # Verify token HMAC( secret_token, user_id )
    secret = settings.app.secret_token.get_secret_value()
    expected = hmac.new(secret.encode(), user_id.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(token, expected):
        return False
    allowed_csv = getattr(settings.app, 'admin_ids', '')
    if not allowed_csv:
        return True
    allowed = set(x.strip() for x in allowed_csv.split(',') if x.strip())
    return user_id in allowed
from src.presentation.web.auth.telegram import validate_telegram_data

routes = web.RouteTableDef()


@routes.get("/api/v1/admin/categories")
async def get_categories(request: web.Request) -> web.Response:
    if not _is_admin(request):
        return web.json_response({"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
    """Возвращает список всех категорий."""
    try:
        container = request.app["dishka_container"]
        async with container(scope=Scope.REQUEST) as req:
            service = await req.get(CategoryService)
            categories = await service.get_all()
        data = [dataclasses.asdict(c) for c in categories]
        return web.json_response(data=data, status=HTTPStatus.OK)
    except Exception as e:
        logging.exception("Ошибка при получении категорий: %s", e)
        return web.json_response(
            {"error": "Internal server error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@routes.post("/api/v1/admin/categories")
async def create_category(request: web.Request) -> web.Response:
    if not _is_admin(request):
        return web.json_response({"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
    try:
        payload = await request.json()
        data = CategoryCreateSchema(**payload)
        container = request.app["dishka_container"]
        async with container(scope=Scope.REQUEST) as req:
            service = await req.get(CategoryService)
            created = await service.create(name=data.name)
        return web.json_response(CategorySchema.model_validate(created).model_dump(), status=HTTPStatus.CREATED)
    except Exception as e:
        logging.exception("Ошибка при создании категории: %s", e)
        return web.json_response({"error": "Internal server error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)


@routes.put("/api/v1/admin/categories/{category_id}")
async def update_category(request: web.Request) -> web.Response:
    if not _is_admin(request):
        return web.json_response({"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
    try:
        category_id = int(request.match_info["category_id"])
        payload = await request.json()
        data = CategoryUpdateSchema(**payload)
        container = request.app["dishka_container"]
        async with container(scope=Scope.REQUEST) as req:
            service = await req.get(CategoryService)
            updated = await service.update(category_id, name=data.name)
        if not updated:
            return web.json_response({"error": "not found"}, status=HTTPStatus.NOT_FOUND)
        return web.json_response(CategorySchema.model_validate(updated).model_dump(), status=HTTPStatus.OK)
    except ValueError:
        return web.json_response({"error": "bad id"}, status=HTTPStatus.BAD_REQUEST)
    except Exception as e:
        logging.exception("Ошибка при обновлении категории: %s", e)
        return web.json_response({"error": "Internal server error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)


@routes.delete("/api/v1/admin/categories/{category_id}")
async def delete_category(request: web.Request) -> web.Response:
    if not _is_admin(request):
        return web.json_response({"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
    try:
        category_id = int(request.match_info["category_id"])
        container = request.app["dishka_container"]
        async with container(scope=Scope.REQUEST) as req:
            service = await req.get(CategoryService)
            ok = await service.delete(category_id)
        if not ok:
            return web.json_response({"error": "not found"}, status=HTTPStatus.NOT_FOUND)
        return web.json_response({"status": "ok"}, status=HTTPStatus.OK)
    except ValueError:
        return web.json_response({"error": "bad id"}, status=HTTPStatus.BAD_REQUEST)
    except Exception as e:
        logging.exception("Ошибка при удалении категории: %s", e)
        return web.json_response({"error": "Internal server error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)


@routes.get("/api/v1/admin/products")
async def get_products(request: web.Request) -> web.Response:
    if not _is_admin(request):
        return web.json_response({"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
    """Возвращает список всех товаров."""
    try:
        container = request.app["dishka_container"]
        async with container(scope=Scope.REQUEST) as req:
            service = await req.get(ProductService)
            products = await service.get_all_products()
        # Сериализуем Decimal -> float через Pydantic
        data = [ProductSchema.model_validate(p).model_dump() for p in products]
        return web.json_response(data=data, status=HTTPStatus.OK)
    except Exception as e:
        logging.exception("Ошибка при получении товаров: %s", e)
        return web.json_response(
            {"error": "Internal server error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@routes.post("/api/v1/admin/products")
async def create_product(request: web.Request) -> web.Response:
    if not _is_admin(request):
        return web.json_response({"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
    try:
        payload = await request.json()
        data = ProductCreateSchema(**payload)
        container = request.app["dishka_container"]
        async with container(scope=Scope.REQUEST) as req:
            service = await req.get(ProductService)
            created = await service.create_product(
                name=data.name,
                description=data.description,
                price=data.price,
                category_id=data.category_id,
            )
        return web.json_response(ProductSchema.model_validate(created).model_dump(), status=HTTPStatus.CREATED)
    except Exception as e:
        logging.exception("Ошибка при создании товара: %s", e)
        return web.json_response({"error": "Internal server error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)


@routes.put("/api/v1/admin/products/{product_id}")
async def update_product(request: web.Request) -> web.Response:
    if not _is_admin(request):
        return web.json_response({"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
    try:
        product_id = int(request.match_info["product_id"])
        payload = await request.json()
        data = ProductUpdateSchema(**payload)
        container = request.app["dishka_container"]
        async with container(scope=Scope.REQUEST) as req:
            service = await req.get(ProductService)
            updated = await service.update_product(
                product_id=product_id,
                name=data.name,
                description=data.description,
                price=data.price,
                category_id=data.category_id,
            )
        if not updated:
            return web.json_response({"error": "not found"}, status=HTTPStatus.NOT_FOUND)
        return web.json_response(ProductSchema.model_validate(updated).model_dump(), status=HTTPStatus.OK)
    except ValueError:
        return web.json_response({"error": "bad id"}, status=HTTPStatus.BAD_REQUEST)
    except Exception as e:
        logging.exception("Ошибка при обновлении товара: %s", e)
        return web.json_response({"error": "Internal server error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)


@routes.delete("/api/v1/admin/products/{product_id}")
async def delete_product(request: web.Request) -> web.Response:
    if not _is_admin(request):
        return web.json_response({"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
    try:
        product_id = int(request.match_info["product_id"])
        container = request.app["dishka_container"]
        async with container(scope=Scope.REQUEST) as req:
            service = await req.get(ProductService)
            ok = await service.delete_product(product_id)
        if not ok:
            return web.json_response({"error": "not found"}, status=HTTPStatus.NOT_FOUND)
        return web.json_response({"status": "ok"}, status=HTTPStatus.OK)
    except ValueError:
        return web.json_response({"error": "bad id"}, status=HTTPStatus.BAD_REQUEST)
    except Exception as e:
        logging.exception("Ошибка при удалении товара: %s", e)
        return web.json_response({"error": "Internal server error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)


@routes.get("/api/v1/admin/products/{product_id}")
async def get_product_by_id(request: web.Request) -> web.Response:
    if not _is_admin(request):
        return web.json_response({"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
    """Возвращает один товар по ID."""
    try:
        product_id = int(request.match_info["product_id"])
        container = request.app["dishka_container"]
        async with container(scope=Scope.REQUEST) as req:
            service = await req.get(ProductService)
            product = await service.get_by_id(product_id)
        if not product:
            return web.json_response(
                {"error": f"Товар с ID {product_id} не найден"},
                status=HTTPStatus.NOT_FOUND
            )
        return web.json_response(data=dataclasses.asdict(product), status=HTTPStatus.OK)
    except ValueError:
        return web.json_response(
            {"error": "Некорректный ID товара"},
            status=HTTPStatus.BAD_REQUEST
        )


@routes.get("/api/v1/admin/orders")
async def admin_get_orders(request: web.Request) -> web.Response:
    if not _is_admin(request):
        return web.json_response({"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
    try:
        container = request.app["dishka_container"]
        async with container(scope=Scope.REQUEST) as req:
            service = await req.get(OrderService)
            uow = service.uow
            orders = await uow.orders.get_all()
        data = [
            {
                "id": o.id,
                "user_id": o.user_id,
                "status": getattr(o.status, "value", str(o.status)),
                "total_amount": float(o.total_amount),
                "created_at": o.created_at.isoformat() if hasattr(o.created_at, "isoformat") else None,
            }
            for o in orders
        ]
        return web.json_response(data=data, status=HTTPStatus.OK)
    except Exception as e:
        logging.exception("Ошибка при получении заказов: %s", e)
        return web.json_response({"error": "Internal server error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
@routes.get("/api/v1/admin/orders/{order_id}")
async def admin_get_order_details(request: web.Request) -> web.Response:
    if not _is_admin(request):
        return web.json_response({"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
    try:
        order_id = int(request.match_info["order_id"])
        container = request.app["dishka_container"]
        async with container(scope=Scope.REQUEST) as req:
            service = await req.get(OrderService)
            uow = service.uow
            order = await uow.orders.get_by_id(order_id)
            if not order:
                return web.json_response({"error": "not found"}, status=HTTPStatus.NOT_FOUND)
            items = await uow.order_items.get_by_order_id(order_id)
        payload = {
            "id": order.id,
            "user_id": order.user_id,
            "status": getattr(order.status, "value", str(order.status)),
            "total_amount": float(order.total_amount),
            "created_at": order.created_at.isoformat() if hasattr(order.created_at, "isoformat") else None,
        }
        payload["items"] = [
            OrderItemSchema(
                product_id=i.product_id,
                quantity=i.quantity,
            ).model_dump() | {"price": float(i.price_at_purchase)}
            for i in items
        ]
        return web.json_response(payload, status=HTTPStatus.OK)
    except ValueError:
        return web.json_response({"error": "bad id"}, status=HTTPStatus.BAD_REQUEST)
    except Exception as e:
        logging.exception("Ошибка при получении деталей заказа: %s", e)
        return web.json_response({"error": "Internal server error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)


@routes.patch("/api/v1/admin/orders/{order_id}")
async def admin_update_order_status(request: web.Request) -> web.Response:
    if not _is_admin(request):
        return web.json_response({"error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
    try:
        order_id = int(request.match_info["order_id"])
        payload = await request.json()
        new_status = payload.get("status")
        if new_status not in ("pending", "paid", "cancelled"):
            return web.json_response({"error": "invalid status"}, status=HTTPStatus.BAD_REQUEST)
        container = request.app["dishka_container"]
        async with container(scope=Scope.REQUEST) as req:
            service = await req.get(OrderService)
            uow = service.uow
            async with uow.atomic():
                updated = await uow.orders.update_status(order_id, new_status)
        if not updated:
            return web.json_response({"error": "not found"}, status=HTTPStatus.NOT_FOUND)
        serialized = {
            "id": updated.id,
            "user_id": updated.user_id,
            "status": getattr(updated.status, "value", str(updated.status)),
            "total_amount": float(updated.total_amount),
            "created_at": updated.created_at.isoformat() if hasattr(updated.created_at, "isoformat") else None,
        }
        return web.json_response(serialized, status=HTTPStatus.OK)
    except ValueError:
        return web.json_response({"error": "bad id"}, status=HTTPStatus.BAD_REQUEST)
    except Exception as e:
        logging.exception("Ошибка при обновлении статуса заказа: %s", e)
        return web.json_response({"error": "Internal server error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)


@routes.post("/api/v1/auth/telegram/validate")
async def auth_validate(request: web.Request) -> web.Response:
    try:
        payload = await request.json()
        result = await validate_telegram_data(payload)
        if result["status"] == "ok":
            return web.json_response(result, status=HTTPStatus.OK)
        return web.json_response(result, status=HTTPStatus.UNAUTHORIZED)
    except Exception as e:
        logging.exception("Ошибка при валидации Telegram WebApp: %s", e)
        return web.json_response(
            {"error": "Internal server error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR
        )
