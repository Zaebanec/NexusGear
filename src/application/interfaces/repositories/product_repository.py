# src/application/interfaces/repositories/product_repository.py - ИСПРАВЛЕННАЯ ВЕРСИЯ

from abc import ABC, abstractmethod

from src.domain.entities.product import Product


class IProductRepository(ABC):
    """
    Абстрактный контракт для работы с данными товаров.
    """

    @abstractmethod
    async def get_by_id(self, product_id: int) -> Product | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_category_id(self, category_id: int) -> list[Product]:
        raise NotImplementedError

    # --- НАЧАЛО ИЗМЕНЕНИЯ ---
    @abstractmethod
    async def get_all(self) -> list[Product]:
        """Возвращает все товары."""
        raise NotImplementedError

    @abstractmethod
    async def add(self, product: Product) -> Product:
        """Создаёт товар и возвращает его с присвоенным идентификатором."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, product: Product) -> Product | None:
        """Обновляет товар; возвращает обновлённый или None, если не найден."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, product_id: int) -> bool:
        """Удаляет товар; возвращает True, если удаление произошло."""
        raise NotImplementedError
    # --- КОНЕЦ ИЗМЕНЕНИЯ ---