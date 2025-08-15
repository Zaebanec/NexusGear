# src/application/services/catalog.py - ОБНОВЛЁННАЯ ВЕРСИЯ

from datetime import datetime
from decimal import Decimal

from src.application.interfaces.repositories.category_repository import (
    ICategoryRepository,
)
from src.application.interfaces.repositories.product_repository import (
    IProductRepository,
)
from src.domain.entities.category import Category
from src.domain.entities.product import Product


class CategoryService:
    """
    Сервис для бизнес-логики, связанной с категориями.
    """
    def __init__(self, category_repo: ICategoryRepository):
        self.category_repo = category_repo

    async def get_all(self) -> list[Category]:
        return await self.category_repo.get_all()

    async def create(self, name: str) -> Category:
        new_category = Category(id=0, name=name)
        return await self.category_repo.add(new_category)

    async def update(self, category_id: int, name: str) -> Category | None:
        return await self.category_repo.update(Category(id=category_id, name=name))

    async def delete(self, category_id: int) -> bool:
        return await self.category_repo.delete(category_id)


class ProductService:
    """
    Сервис для бизнес-логики, связанной с товарами.
    """
    def __init__(
        self,
        product_repo: IProductRepository,
        category_repo: ICategoryRepository,
    ):
        self.product_repo = product_repo
        self.category_repo = category_repo

    async def get_all_products(self) -> list[Product]:
        """Возвращает все товары."""
        return await self.product_repo.get_all()

    async def get_by_category(self, category_id: int) -> list[Product]:
        return await self.product_repo.get_by_category_id(category_id)

    async def get_by_id(self, product_id: int) -> Product | None:
        """Возвращает один товар по его ID."""
        return await self.product_repo.get_by_id(product_id)

    async def create_product(
        self,
        name: str,
        description: str,
        price: Decimal,
        category_id: int,
    ) -> Product:
        category = await self.category_repo.get_by_id(category_id)
        if not category:
            raise ValueError(f"Категория с ID {category_id} не найдена.")

        new_product = Product(
            id=0,
            name=name,
            description=description,
            price=price,
            category_id=category_id,
            created_at=datetime.utcnow(),
        )
        return await self.product_repo.add(new_product)

    async def update_product(
        self,
        product_id: int,
        name: str,
        description: str,
        price: Decimal,
        category_id: int,
    ) -> Product | None:
        category = await self.category_repo.get_by_id(category_id)
        if not category:
            raise ValueError(f"Категория с ID {category_id} не найдена.")
        return await self.product_repo.update(
            Product(
                id=product_id,
                name=name,
                description=description,
                price=price,
                category_id=category_id,
                created_at=datetime.utcnow(),
            )
        )

    async def delete_product(self, product_id: int) -> bool:
        return await self.product_repo.delete(product_id)
