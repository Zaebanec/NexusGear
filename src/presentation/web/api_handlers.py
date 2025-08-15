# src/presentation/web/api_handlers.py

import dataclasses
import logging
from http import HTTPStatus

from aiohttp import web

from src.application.services.catalog import CategoryService, ProductService
from src.presentation.web.auth.telegram import validate_telegram_data

routes = web.RouteTableDef()


@routes.get("/api/v1/admin/categories")
async def get_categories(request: web.Request) -> web.Response:
    """Возвращает список всех категорий."""
    try:
        container = request.app["dishka_container"]
        service = await container.get(CategoryService)
        categories = await service.get_all()
        data = [dataclasses.asdict(c) for c in categories]
        return web.json_response(data=data, status=HTTPStatus.OK)
    except Exception as e:
        logging.exception("Ошибка при получении категорий: %s", e)
        return web.json_response(
            {"error": "Internal server error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@routes.get("/api/v1/admin/products")
async def get_products(request: web.Request) -> web.Response:
    """Возвращает список всех товаров."""
    try:
        container = request.app["dishka_container"]
        service = await container.get(ProductService)
        products = await service.get_all_products()
        data = [dataclasses.asdict(p) for p in products]
        return web.json_response(data=data, status=HTTPStatus.OK)
    except Exception as e:
        logging.exception("Ошибка при получении товаров: %s", e)
        return web.json_response(
            {"error": "Internal server error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@routes.get("/api/v1/admin/products/{product_id}")
async def get_product_by_id(request: web.Request) -> web.Response:
    """Возвращает один товар по ID."""
    try:
        product_id = int(request.match_info["product_id"])
        container = request.app["dishka_container"]
        service = await container.get(ProductService)
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
