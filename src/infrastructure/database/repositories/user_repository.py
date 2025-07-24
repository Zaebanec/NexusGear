# src/infrastructure/database/repositories/user_repository.py

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repositories.user_repository import IUserRepository
from src.domain.entities.user import User as DomainUser
from src.infrastructure.database.models.user import User as DbUser


def _to_domain_user(db_user: DbUser) -> DomainUser:
    """Маппер для преобразования модели БД в доменную сущность."""
    return DomainUser(
        id=db_user.id,
        telegram_id=db_user.telegram_id,
        full_name=db_user.full_name,
        username=db_user.username,
        created_at=db_user.created_at,
    )


class UserRepository(IUserRepository):
    """
    Реализация репозитория для пользователей, работающая с PostgreSQL через SQLAlchemy.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> DomainUser | None:
        stmt = select(DbUser).where(DbUser.id == user_id)
        db_user = await self.session.scalar(stmt)
        return _to_domain_user(db_user) if db_user else None

    async def get_by_telegram_id(self, telegram_id: int) -> DomainUser | None:
        stmt = select(DbUser).where(DbUser.telegram_id == telegram_id)
        db_user = await self.session.scalar(stmt)
        return _to_domain_user(db_user) if db_user else None

    async def add(self, user: DomainUser) -> DomainUser:
        """
        Добавляет нового пользователя в сессию, выполняет flush для получения ID
        и возвращает актуальную доменную сущность.
        """
        db_user = DbUser(
            telegram_id=user.telegram_id,
            full_name=user.full_name,
            username=user.username,
        )
        self.session.add(db_user)
        # Принудительно отправляем запрос в БД, чтобы сгенерировался ID
        await self.session.flush()
        # Обновляем объект из БД, чтобы получить все поля (например, created_at)
        await self.session.refresh(db_user)
        # Возвращаем доменную сущность с реальными данными из БД
        return _to_domain_user(db_user)