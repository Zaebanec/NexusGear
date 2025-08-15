from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repositories.category_repository import (
    ICategoryRepository,
)
from src.domain.entities.category import Category as DomainCategory
from src.infrastructure.database.models.category import Category as DbCategory


def _to_domain_category(db_category: DbCategory) -> DomainCategory:
    """Маппер для преобразования модели БД в доменную сущность."""
    return DomainCategory(id=db_category.id, name=db_category.name)


class CategoryRepository(ICategoryRepository):
    """
    Реализация репозитория для категорий.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, category_id: int) -> DomainCategory | None:
        stmt = select(DbCategory).where(DbCategory.id == category_id)
        db_category = await self.session.scalar(stmt)
        return _to_domain_category(db_category) if db_category else None

    async def get_all(self) -> list[DomainCategory]:
        stmt = select(DbCategory).order_by(DbCategory.name)
        result = await self.session.scalars(stmt)
        return [_to_domain_category(c) for c in result.all()]

    async def add(self, category: DomainCategory) -> DomainCategory:
        db = DbCategory(name=category.name)
        self.session.add(db)
        await self.session.flush()
        await self.session.refresh(db)
        return _to_domain_category(db)

    async def update(self, category: DomainCategory) -> DomainCategory | None:
        stmt = (
            update(DbCategory)
            .where(DbCategory.id == category.id)
            .values(name=category.name)
            .returning(DbCategory)
        )
        db = await self.session.scalar(stmt)
        return _to_domain_category(db) if db else None

    async def delete(self, category_id: int) -> bool:
        stmt = delete(DbCategory).where(DbCategory.id == category_id)
        result = await self.session.execute(stmt)
        # result.rowcount может быть None в некоторых драйверах; проверяем через deleted primary key
        return bool(result.rowcount and result.rowcount > 0)