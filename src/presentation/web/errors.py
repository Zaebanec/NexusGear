# src/presentation/web/errors.py

from __future__ import annotations

from typing import Any, Optional
from aiohttp import web


def json_error(
    message: str,
    *,
    code: str = "bad_request",
    status: int = 400,
    details: Optional[dict[str, Any]] = None,
) -> web.Response:
    payload: dict[str, Any] = {"error": {"code": code, "message": message}}
    if details:
        payload["error"]["details"] = details
    return web.json_response(payload, status=status)


