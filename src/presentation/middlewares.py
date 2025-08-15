# src/presentation/middlewares.py

import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class LoggingMiddleware(BaseMiddleware):
    """
    Промежуточный слой для логирования всех входящих обновлений.
    """
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Просто выводим в лог все содержимое объекта Update
        # Используем to_python() для более чистого вывода
        logging.info(f"--- CAPTURED UPDATE ---\n{event.model_dump_json(indent=2)}")

        # Передаем управление дальше по цепочке middleware и хендлеров
        return await handler(event, data)
