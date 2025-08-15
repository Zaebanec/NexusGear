# src/presentation/web/middlewares.py

from __future__ import annotations

import time
from collections import deque
from typing import Deque, Dict, Tuple

from aiohttp import web


def admin_rate_limit_middleware(
    *, window_seconds: int = 60, max_requests: int = 120
):
    """
    Простой in-memory rate limit для админских эндпоинтов `/api/v1/admin/*`.

    Ключ rate limit: (X-Admin-User || IP, path-prefix).
    Ограничение по умолчанию: 120 запросов за 60 секунд на ключ.
    """

    buckets: Dict[Tuple[str, str], Deque[float]] = {}

    @web.middleware
    async def _middleware(request: web.Request, handler):
        path: str = request.path
        if not path.startswith("/api/v1/admin"):
            return await handler(request)

        now = time.time()
        admin_user = request.headers.get("X-Admin-User") or request.remote or "unknown"
        key = (str(admin_user), "/api/v1/admin")

        dq = buckets.get(key)
        if dq is None:
            dq = deque()
            buckets[key] = dq

        # очистка окна
        threshold = now - window_seconds
        while dq and dq[0] < threshold:
            dq.popleft()

        if len(dq) >= max_requests:
            return web.json_response(
                {
                    "error": "rate_limited",
                    "message": "Too many requests. Please try again later.",
                },
                status=429,
            )

        dq.append(now)
        return await handler(request)

    return _middleware



