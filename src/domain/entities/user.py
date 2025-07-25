# src/domain/entities/user.py - ФИНАЛЬНАЯ ВЕРСИЯ

from dataclasses import dataclass, field
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
    
    # --- КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ: Автоматическая установка времени создания ---
    # Мы используем default_factory, чтобы datetime.utcnow вызывался
    # каждый раз при создании нового экземпляра.
    # Использование UTC - лучшая практика для серверного времени.
    created_at: datetime = field(default_factory=datetime.utcnow)