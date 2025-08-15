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

    @abstractmethod
    async def add(self, category: Category) -> Category:
        """Создаёт новую категорию и возвращает её с присвоенным идентификатором."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, category: Category) -> Category | None:
        """Обновляет категорию; возвращает обновлённую или None, если не найдена."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, category_id: int) -> bool:
        """Удаляет категорию; возвращает True, если удаление произошло."""
        raise NotImplementedError