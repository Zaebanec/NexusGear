from aiohttp import web
from dishka.async_container import AsyncContainer

from .api_handlers import routes


def setup_app(dishka_container: AsyncContainer) -> web.Application:
    """
    Создает и настраивает экземпляр веб-приложения AIOHTTP.
    """
    app = web.Application()

    # Сохраняем DI-контейнер в приложении, чтобы он был доступен в обработчиках
    app["dishka_container"] = dishka_container

    # Регистрируем роуты API
    app.add_routes(routes)

    # Настраиваем раздачу статических файлов для админ-панели
    app.router.add_static(
        "/static/", path="src/presentation/web/static", name="static"
    )
    # Отдаем admin.html по корневому маршруту
    app.router.add_get(
        "/", lambda req: web.FileResponse("src/presentation/web/static/admin.html")
    )

    return app