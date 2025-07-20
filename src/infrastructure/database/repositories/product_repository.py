from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repositories.product_repository import (
    IProductRepository,
)
from src.domain.entities.product import Product as DomainProduct
from src.infrastructure.database.models.product import Product as DbProduct


def _to_domain_product(db_product: DbProduct) -> DomainProduct:
    """Маппер для преобразования модели БД в доменную сущность."""
    return DomainProduct(
        id=db_product.id,
        name=db_product.name,
        description=db_product.description,
        price=db_product.price,
        category_id=db_product.category_id,
        created_at=db_product.created_at,
    )


class ProductRepository(IProductRepository):
    """
    Реализация репозитория для товаров.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, product_id: int) -> DomainProduct | None:
        stmt = select(DbProduct).where(DbProduct.id == product_id)
        db_product = await self.session.scalar(stmt)
        return _to_domain_product(db_product) if db_product else None

    # --- НАЧАЛО ИСПРАВЛЕНИЯ ---
    async def get_by_category_id(self, category_id: int) -> list[DomainProduct]:
        stmt = select(DbProduct).where(DbProduct.category_id == category_id)
        result = await self.session.scalars(stmt)
        return [_to_domain_product(p) for p in result.all()]
    # --- КОНЕЦ ИСПРАВЛЕНИЯ ---