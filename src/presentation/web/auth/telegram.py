from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any, Dict

from pydantic import BaseModel

from src.infrastructure.config import settings


class TelegramInitData(BaseModel):
    hash: str
    auth_date: str | None = None
    query_id: str | None = None
    user: dict[str, Any] | None = None
    start_param: str | None = None
    can_send_after: int | None = None


def _check_signature(data: Dict[str, Any]) -> bool:
    received_hash = data.pop("hash", "")
    token = settings.bot.token.get_secret_value()
    secret_key = hashlib.sha256(token.encode()).digest()
    check_string = "\n".join(
        f"{k}={data[k]}" for k in sorted(data.keys()) if data[k] is not None
    )
    calculated_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(received_hash, calculated_hash)


async def validate_telegram_data(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        parsed = TelegramInitData(**payload)
        data = json.loads(json.dumps(payload))
        if not _check_signature(data):
            return {"status": "error", "message": "invalid_signature"}

        user = parsed.user or {}
        user_id_raw = user.get("id")
        telegram_id = int(user_id_raw) if user_id_raw is not None else None
        if telegram_id is None:
            return {"status": "error", "message": "missing_user"}

        # Produce a simple JWT-like opaque token without leaking secrets
        # In a real app, use proper JWT lib. Here we return a stub for e2e flow.
        token_seed = f"{telegram_id}:{parsed.auth_date or ''}"
        token = hashlib.sha256(token_seed.encode()).hexdigest()
        return {"status": "ok", "user_id": telegram_id, "token": token}
    except Exception:
        return {"status": "error", "message": "invalid_payload"}


