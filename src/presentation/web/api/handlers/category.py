# src/presentation/web/api/handlers/category.py

from aiohttp import web
from dishka import AsyncContainer, Scope

from src.application.services.catalog import CategoryService
from src.presentation.web.api.schemas.category import CategorySchema
from src.presentation.web.app_keys import APP_DISHKA_CONTAINER

async def get_categories(request: web.Request) -> web.Response:
    """
    Эндпоинт для получения списка всех категорий.
    GET /api/categories
    """
    dishka_container: AsyncContainer = request.app[APP_DISHKA_CONTAINER]
    
    async with dishka_container(scope=Scope.REQUEST) as request_container:
        category_service = await request_container.get(CategoryService)
        categories = await category_service.get_all()

        # Сериализуем SQLAlchemy-объекты в JSON с помощью Pydantic-схемы
        response_data = [CategorySchema.model_validate(cat).model_dump() for cat in categories]
        
        return web.json_response(response_data)