# src/presentation/web/api_handlers.py

import dataclasses
import logging
from http import HTTPStatus

from aiohttp import web
from decimal import Decimal
from dishka import Scope

from src.application.services.catalog import CategoryService, ProductService
from src.application.services.order_service import OrderService
from src.presentation.web.api.schemas.product import (
    ProductSchema,
    ProductCreateSchema,
    ProductUpdateSchema,
)
from src.infrastructure.config import settings
import hashlib
import hmac
from src.presentation.web.api.schemas.order import OrderItemSchema
from src.presentation.web.api.schemas.category import (
    CategorySchema,
    CategoryCreateSchema,
    CategoryUpdateSchema,
)
from src.presentation.web.errors import json_error
from pydantic import ValidationError
from src.presentation.web.auth.telegram import validate_telegram_data
from src.presentation.web.app_keys import APP_DISHKA_CONTAINER
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
from src.presentation.web.app_keys import APP_DISHKA_CONTAINER

routes = web.RouteTableDef()


def _parse_pagination(request: web.Request) -> tuple[int, int, str | None]:
    q = request.rel_url.query.get("q")
    try:
        limit = int(request.rel_url.query.get("limit", "0"))
        offset = int(request.rel_url.query.get("offset", "0"))
    except ValueError:
        limit, offset = 0, 0
    if limit < 0:
        limit = 0
    if offset < 0:
        offset = 0
    return limit, offset, (q or None)

def _apply_pagination_and_headers(
    request: web.Request,
    data_list: list,
    *,
    limit: int,
    offset: int,
) -> web.Response:
    total = len(data_list)
    if limit:
        sliced = data_list[offset : offset + limit]
    else:
        sliced = data_list
    resp = web.json_response(data=sliced, status=HTTPStatus.OK)
    resp.headers["X-Total-Count"] = str(total)
    resp.headers["X-Limit"] = str(limit)
    resp.headers["X-Offset"] = str(offset)
    return resp


@routes.get("/api/v1/admin/categories")
async def get_categories(request: web.Request) -> web.Response:
    if not _is_admin(request):
        return json_error("Unauthorized", code="unauthorized", status=HTTPStatus.UNAUTHORIZED)
    """Возвращает список всех категорий."""
    try:
        container = request.app[APP_DISHKA_CONTAINER]
        async with container(scope=Scope.REQUEST) as req:
            service = await req.get(CategoryService)
            categories = await service.get_all()
        limit, offset, q = _parse_pagination(request)
        items = categories
        if q:
            ql = q.lower()
            items = [
                c
                for c in items
                if ql in str(getattr(c, "id", "")).lower()
                or ql in str(getattr(c, "name", getattr(c, "title", ""))).lower()
            ]
        data = [dataclasses.asdict(c) for c in items]
        return _apply_pagination_and_headers(request, data, limit=limit, offset=offset)
    except Exception as e:
        logging.exception("Ошибка при получении категорий: %s", e)
        return json_error("Internal server error", code="internal_error", status=HTTPStatus.INTERNAL_SERVER_ERROR)


@routes.post("/api/v1/admin/categories")
async def create_category(request: web.Request) -> web.Response:
    if not _is_admin(request):
        return json_error("Unauthorized", code="unauthorized", status=HTTPStatus.UNAUTHORIZED)
    try:
        payload = await request.json()
        try:
            data = CategoryCreateSchema(**payload)
        except ValidationError as ve:
            return json_error("Bad request", code="bad_request", status=HTTPStatus.BAD_REQUEST, details={"errors": ve.errors()})
        container = request.app[APP_DISHKA_CONTAINER]
        async with container(scope=Scope.REQUEST) as req:
            service = await req.get(CategoryService)
            created = await service.create(name=data.name)
        return web.json_response(CategorySchema.model_validate(created).model_dump(), status=HTTPStatus.CREATED)
    except Exception as e:
        logging.exception("Ошибка при создании категории: %s", e)
        return json_error("Internal server error", code="internal_error", status=HTTPStatus.INTERNAL_SERVER_ERROR)


@routes.put("/api/v1/admin/categories/{category_id}")
async def update_category(request: web.Request) -> web.Response:
    if not _is_admin(request):
        return json_error("Unauthorized", code="unauthorized", status=HTTPStatus.UNAUTHORIZED)
    try:
        category_id = int(request.match_info["category_id"])
        payload = await request.json()
        try:
            data = CategoryUpdateSchema(**payload)
        except ValidationError as ve:
            return json_error("Bad request", code="bad_request", status=HTTPStatus.BAD_REQUEST, details={"errors": ve.errors()})
        container = request.app[APP_DISHKA_CONTAINER]
        async with container(scope=Scope.REQUEST) as req:
            service = await req.get(CategoryService)
            updated = await service.update(category_id, name=data.name)
        if not updated:
            return json_error("Not found", code="not_found", status=HTTPStatus.NOT_FOUND)
        return web.json_response(CategorySchema.model_validate(updated).model_dump(), status=HTTPStatus.OK)
    except ValueError:
        return json_error("Bad id", code="bad_request", status=HTTPStatus.BAD_REQUEST)
    except Exception as e:
        logging.exception("Ошибка при обновлении категории: %s", e)
        return json_error("Internal server error", code="internal_error", status=HTTPStatus.INTERNAL_SERVER_ERROR)


@routes.delete("/api/v1/admin/categories/{category_id}")
async def delete_category(request: web.Request) -> web.Response:
    if not _is_admin(request):
        return json_error("Unauthorized", code="unauthorized", status=HTTPStatus.UNAUTHORIZED)
    try:
        category_id = int(request.match_info["category_id"])
        container = request.app[APP_DISHKA_CONTAINER]
        async with container(scope=Scope.REQUEST) as req:
            service = await req.get(CategoryService)
            ok = await service.delete(category_id)
        if not ok:
            return json_error("Not found", code="not_found", status=HTTPStatus.NOT_FOUND)
        return web.json_response({"status": "ok"}, status=HTTPStatus.OK)
    except ValueError:
        return json_error("Bad id", code="bad_request", status=HTTPStatus.BAD_REQUEST)
    except Exception as e:
        logging.exception("Ошибка при удалении категории: %s", e)
        return json_error("Internal server error", code="internal_error", status=HTTPStatus.INTERNAL_SERVER_ERROR)


@routes.get("/api/v1/admin/products")
async def get_products(request: web.Request) -> web.Response:
    if not _is_admin(request):
        return json_error("Unauthorized", code="unauthorized", status=HTTPStatus.UNAUTHORIZED)
    """Возвращает список всех товаров."""
    try:
        container = request.app[APP_DISHKA_CONTAINER]
        async with container(scope=Scope.REQUEST) as req:
            service = await req.get(ProductService)
            products = await service.get_all_products()
        limit, offset, q = _parse_pagination(request)
        items = products
        # category filter
        cat_q = request.rel_url.query.get("category_id")
        if cat_q is not None:
            try:
                cat_id = int(cat_q)
                items = [p for p in items if getattr(p, "category_id", None) == cat_id]
            except ValueError:
                pass
        if q:
            ql = q.lower()
            def _p(p):
                return (
                    ql in str(getattr(p, "id", "")).lower()
                    or ql in str(getattr(p, "name", "")).lower()
                    or ql in str(getattr(p, "description", "")).lower()
                    or ql in str(getattr(p, "category_id", "")).lower()
                )
            items = [p for p in items if _p(p)]
        data = [ProductSchema.model_validate(p).model_dump() for p in items]
        return _apply_pagination_and_headers(request, data, limit=limit, offset=offset)
    except Exception as e:
        logging.exception("Ошибка при получении товаров: %s", e)
        return json_error("Internal server error", code="internal_error", status=HTTPStatus.INTERNAL_SERVER_ERROR)


@routes.post("/api/v1/admin/products")
async def create_product(request: web.Request) -> web.Response:
    if not _is_admin(request):
        return json_error("Unauthorized", code="unauthorized", status=HTTPStatus.UNAUTHORIZED)
    try:
        payload = await request.json()
        try:
            data = ProductCreateSchema(**payload)
        except ValidationError as ve:
            return json_error("Bad request", code="bad_request", status=HTTPStatus.BAD_REQUEST, details={"errors": ve.errors()})
        container = request.app[APP_DISHKA_CONTAINER]
        async with container(scope=Scope.REQUEST) as req:
            service = await req.get(ProductService)
            created = await service.create_product(
                name=data.name,
                description=data.description,
                price=Decimal(str(data.price)),
                category_id=data.category_id,
            )
        return web.json_response(ProductSchema.model_validate(created).model_dump(), status=HTTPStatus.CREATED)
    except Exception as e:
        logging.exception("Ошибка при создании товара: %s", e)
        return json_error("Internal server error", code="internal_error", status=HTTPStatus.INTERNAL_SERVER_ERROR)


@routes.put("/api/v1/admin/products/{product_id}")
async def update_product(request: web.Request) -> web.Response:
    if not _is_admin(request):
        return json_error("Unauthorized", code="unauthorized", status=HTTPStatus.UNAUTHORIZED)
    try:
        product_id = int(request.match_info["product_id"])
        payload = await request.json()
        try:
            data = ProductUpdateSchema(**payload)
        except ValidationError as ve:
            return json_error("Bad request", code="bad_request", status=HTTPStatus.BAD_REQUEST, details={"errors": ve.errors()})
        container = request.app[APP_DISHKA_CONTAINER]
        async with container(scope=Scope.REQUEST) as req:
            service = await req.get(ProductService)
            updated = await service.update_product(
                product_id=product_id,
                name=data.name,
                description=data.description,
                price=Decimal(str(data.price)),
                category_id=data.category_id,
            )
        if not updated:
            return json_error("Not found", code="not_found", status=HTTPStatus.NOT_FOUND)
        return web.json_response(ProductSchema.model_validate(updated).model_dump(), status=HTTPStatus.OK)
    except ValueError:
        return json_error("Bad id", code="bad_request", status=HTTPStatus.BAD_REQUEST)
    except Exception as e:
        logging.exception("Ошибка при обновлении товара: %s", e)
        return json_error("Internal server error", code="internal_error", status=HTTPStatus.INTERNAL_SERVER_ERROR)


@routes.delete("/api/v1/admin/products/{product_id}")
async def delete_product(request: web.Request) -> web.Response:
    if not _is_admin(request):
        return json_error("Unauthorized", code="unauthorized", status=HTTPStatus.UNAUTHORIZED)
    try:
        product_id = int(request.match_info["product_id"])
        container = request.app[APP_DISHKA_CONTAINER]
        async with container(scope=Scope.REQUEST) as req:
            service = await req.get(ProductService)
            ok = await service.delete_product(product_id)
        if not ok:
            return json_error("Not found", code="not_found", status=HTTPStatus.NOT_FOUND)
        return web.json_response({"status": "ok"}, status=HTTPStatus.OK)
    except ValueError:
        return json_error("Bad id", code="bad_request", status=HTTPStatus.BAD_REQUEST)
    except Exception as e:
        logging.exception("Ошибка при удалении товара: %s", e)
        return json_error("Internal server error", code="internal_error", status=HTTPStatus.INTERNAL_SERVER_ERROR)


@routes.get("/api/v1/admin/products/{product_id}")
async def get_product_by_id(request: web.Request) -> web.Response:
    if not _is_admin(request):
        return json_error("Unauthorized", code="unauthorized", status=HTTPStatus.UNAUTHORIZED)
    """Возвращает один товар по ID."""
    try:
        product_id = int(request.match_info["product_id"])
        container = request.app[APP_DISHKA_CONTAINER]
        async with container(scope=Scope.REQUEST) as req:
            service = await req.get(ProductService)
            product = await service.get_by_id(product_id)
        if not product:
            return json_error("Not found", code="not_found", status=HTTPStatus.NOT_FOUND)
        return web.json_response(data=dataclasses.asdict(product), status=HTTPStatus.OK)
    except ValueError:
        return json_error("Bad id", code="bad_request", status=HTTPStatus.BAD_REQUEST)


@routes.get("/api/v1/admin/orders")
async def admin_get_orders(request: web.Request) -> web.Response:
    if not _is_admin(request):
        return json_error("Unauthorized", code="unauthorized", status=HTTPStatus.UNAUTHORIZED)
    try:
        container = request.app[APP_DISHKA_CONTAINER]
        async with container(scope=Scope.REQUEST) as req:
            service = await req.get(OrderService)
            uow = service.uow
            orders = await uow.orders.get_all()
        limit, offset, q = _parse_pagination(request)
        items = orders
        # status filter
        status_q = request.rel_url.query.get("status")
        if status_q:
            items = [
                o for o in items
                if str(getattr(o, "status", "")) == status_q or getattr(o, "status", None) and getattr(o.status, "value", str(o.status)) == status_q
            ]
        # date range filters
        from datetime import datetime
        cf = request.rel_url.query.get("created_from")
        ct = request.rel_url.query.get("created_to")
        created_from = None
        created_to = None
        try:
            if cf:
                created_from = datetime.fromisoformat(cf)
        except Exception:
            created_from = None
        try:
            if ct:
                created_to = datetime.fromisoformat(ct)
        except Exception:
            created_to = None
        if created_from or created_to:
            def _in_range(o):
                ts = getattr(o, "created_at", None)
                if not ts or not hasattr(ts, "__class__"):
                    return False
                if created_from and ts < created_from:
                    return False
                if created_to and ts > created_to:
                    return False
                return True
            items = [o for o in items if _in_range(o)]
        if q:
            ql = q.lower()
            items = [
                o for o in items
                if ql in str(getattr(o, "id", "")).lower()
                or ql in str(getattr(o, "user_id", "")).lower()
                or ql in str(getattr(o, "status", "")).lower()
            ]
        data = [
            {
                "id": o.id,
                "user_id": o.user_id,
                "status": getattr(o.status, "value", str(o.status)),
                "total_amount": float(o.total_amount),
                "created_at": o.created_at.isoformat() if hasattr(o.created_at, "isoformat") else None,
            }
            for o in items
        ]
        return _apply_pagination_and_headers(request, data, limit=limit, offset=offset)
    except Exception as e:
        logging.exception("Ошибка при получении заказов: %s", e)
        return json_error("Internal server error", code="internal_error", status=HTTPStatus.INTERNAL_SERVER_ERROR)
@routes.get("/api/v1/admin/orders/{order_id}")
async def admin_get_order_details(request: web.Request) -> web.Response:
    if not _is_admin(request):
        return json_error("Unauthorized", code="unauthorized", status=HTTPStatus.UNAUTHORIZED)
    try:
        order_id = int(request.match_info["order_id"])
        container = request.app[APP_DISHKA_CONTAINER]
        async with container(scope=Scope.REQUEST) as req:
            service = await req.get(OrderService)
            uow = service.uow
            order = await uow.orders.get_by_id(order_id)
            if not order:
                return json_error("Not found", code="not_found", status=HTTPStatus.NOT_FOUND)
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
        return json_error("Bad id", code="bad_request", status=HTTPStatus.BAD_REQUEST)
    except Exception as e:
        logging.exception("Ошибка при получении деталей заказа: %s", e)
        return json_error("Internal server error", code="internal_error", status=HTTPStatus.INTERNAL_SERVER_ERROR)


@routes.patch("/api/v1/admin/orders/{order_id}")
async def admin_update_order_status(request: web.Request) -> web.Response:
    if not _is_admin(request):
        return json_error("Unauthorized", code="unauthorized", status=HTTPStatus.UNAUTHORIZED)
    try:
        order_id = int(request.match_info["order_id"])
        payload = await request.json()
        new_status = payload.get("status")
        if new_status not in ("pending", "paid", "cancelled"):
            return json_error("Invalid status", code="bad_request", status=HTTPStatus.BAD_REQUEST)
        container = request.app[APP_DISHKA_CONTAINER]
        async with container(scope=Scope.REQUEST) as req:
            service = await req.get(OrderService)
            uow = service.uow
            async with uow.atomic():
                updated = await uow.orders.update_status(order_id, new_status)
        if not updated:
            return json_error("Not found", code="not_found", status=HTTPStatus.NOT_FOUND)
        serialized = {
            "id": updated.id,
            "user_id": updated.user_id,
            "status": getattr(updated.status, "value", str(updated.status)),
            "total_amount": float(updated.total_amount),
            "created_at": updated.created_at.isoformat() if hasattr(updated.created_at, "isoformat") else None,
        }
        return web.json_response(serialized, status=HTTPStatus.OK)
    except ValueError:
        return json_error("Bad id", code="bad_request", status=HTTPStatus.BAD_REQUEST)
    except Exception as e:
        logging.exception("Ошибка при обновлении статуса заказа: %s", e)
        return json_error("Internal server error", code="internal_error", status=HTTPStatus.INTERNAL_SERVER_ERROR)


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
        return json_error("Internal server error", code="internal_error", status=HTTPStatus.INTERNAL_SERVER_ERROR)
