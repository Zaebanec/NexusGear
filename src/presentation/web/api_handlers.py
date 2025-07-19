import dataclasses
import logging
from http import HTTPStatus

from aiohttp import web

from src.application.services.catalog import CategoryService, ProductService

routes = web.RouteTableDef()


@routes.get("/api/v1/admin/categories")
async def get_categories(request: web.Request) -> web.Response:
    """Возвращает список всех категорий."""
    try:
        container = request.app["dishka_container"]
        service = await container.get(CategoryService)
        categories = await service.get_all()
        # Сериализуем dataclass'ы в словари для JSON-ответа
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
        # ПРИМЕЧАНИЕ: Метод get_all_products() еще не определен.
        # Мы добавим его в сервисы и репозитории.
        # Пока что представим, что он существует.
        products = await service.get_all_products()
        data = [dataclasses.asdict(p) for p in products]
        return web.json_response(data=data, status=HTTPStatus.OK)
    except Exception as e:
        logging.exception("Ошибка при получении товаров: %s", e)
        return web.json_response(
            {"error": "Internal server error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR
        )