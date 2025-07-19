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

# --- НАЧАЛО ИСПРАВЛЕНИЯ ---
# СТРОКА НИЖЕ БЫЛА УДАЛЕНА, ТАК КАК ФАЙЛ НЕ МОЖЕТ ИМПОРТИРОВАТЬ ИЗ САМОГО СЕБЯ
# from src.application.services.catalog import CategoryService, ProductService
# --- КОНЕЦ ИСПРАВЛЕНИЯ ---


class CategoryService:
    """
    Сервис для бизнес-логики, связанной с категориями.
    """
    def __init__(self, category_repo: ICategoryRepository):
        self.category_repo = category_repo

    async def get_all(self) -> list[Category]:
        return await self.category_repo.get_all()


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

    async def get_by_category(self, category_id: int) -> list[Product]:
        # Примечание: Мы еще не реализовали этот метод в репозитории.
        # Чтобы избежать ошибок, пока вернем пустой список.
        # return await self.product_repo.get_by_category_id(category_id)
        return []

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

        # await self.product_repo.add(new_product)
        return new_product