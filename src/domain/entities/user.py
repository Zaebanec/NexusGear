from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """
    Доменная сущность 'Пользователь'.

    Представляет пользователя системы, взаимодействующего с ботом.
    """
    id: int
    telegram_id: int
    full_name: str
    username: Optional[str]
    created_at: datetime