# src/presentation/web/api/handlers/product.py

from aiohttp import web
from dishka import AsyncContainer, Scope

from src.application.services.catalog import ProductService
from src.presentation.web.api.schemas.product import ProductSchema
from src.presentation.web.app_keys import APP_DISHKA_CONTAINER

async def get_products_by_category(request: web.Request) -> web.Response:
    """
    Эндпоинт для получения списка товаров по ID категории.
    GET /api/products?category_id=<ID_КАТЕГОРИИ>
    """
    try:
        category_id = int(request.rel_url.query['category_id'])
    except (ValueError, KeyError):
        return web.json_response({'error': 'Invalid or missing category_id'}, status=400)

    dishka_container: AsyncContainer = request.app[APP_DISHKA_CONTAINER]
    async with dishka_container(scope=Scope.REQUEST) as request_container:
        product_service = await request_container.get(ProductService)
        products = await product_service.get_by_category(category_id)

        response_data = [ProductSchema.model_validate(p).model_dump() for p in products]
        return web.json_response(response_data)
