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
        return await self.product_repo.get_by_category_id(category_id)

    async def create_product(
        self,
        name: str,
        description: str,
        price: Decimal,
        category_id: int,
    ) -> Product:
        # Валидация: проверяем, существует ли такая категория
        category = await self.category_repo.get_by_id(category_id)
        if not category:
            raise ValueError(f"Категория с ID {category_id} не найдена.")

        # Создаем доменную сущность.
        # ID и created_at будут присвоены на уровне БД,
        # поэтому здесь мы их не устанавливаем.
        new_product = Product(
            id=0,  # Временный ID
            name=name,
            description=description,
            price=price,
            category_id=category_id,
            created_at=datetime.utcnow(), # Временная метка
        )

        await self.product_repo.add(new_product)
        # Примечание: для получения продукта с ID, присвоенным БД,
        # потребуется реализация паттерна Unit of Work, который
        # выполнит flush сессии. На данном этапе мы возвращаем
        # созданный объект без реального ID.

        return new_product