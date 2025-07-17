from abc import ABC, abstractmethod

from src.domain.entities.category import Category


class ICategoryRepository(ABC):
    """
    Абстрактный контракт для работы с данными категорий.
    """

    @abstractmethod
    async def get_by_id(self, category_id: int) -> Category | None:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list[Category]:
        raise NotImplementedError