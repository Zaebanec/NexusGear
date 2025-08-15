from abc import ABC, abstractmethod

from src.domain.entities.user import User


class IUserRepository(ABC):
    """
    Абстрактный контракт для работы с данными пользователей.
    """

    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def add(self, user: User) -> User:
        raise NotImplementedError