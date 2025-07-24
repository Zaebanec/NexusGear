# src/application/services/user_service.py

from src.application.contracts.persistence.uow import IUnitOfWork
from src.application.interfaces.repositories.user_repository import IUserRepository
from src.domain.entities.user import User as DomainUser

class UserService:
    def __init__(self, user_repo: IUserRepository, uow: IUnitOfWork):
        self.user_repo = user_repo
        self.uow = uow

    async def register_user_if_not_exists(
        self,
        telegram_id: int,
        full_name: str,
        username: str | None,
    ) -> DomainUser:
        # Оборачиваем всю логику в атомарную транзакцию
        async with self.uow.atomic():
            existing_user = await self.user_repo.get_by_telegram_id(telegram_id)
            if existing_user:
                return existing_user

            new_user_data = DomainUser(
                id=0,  # ID будет сгенерирован БД
                telegram_id=telegram_id,
                full_name=full_name,
                username=username,
                created_at=None # Будет установлено БД
            )
            # Вызываем обновленный метод add и получаем сущность с реальным ID
            persisted_user = await self.user_repo.add(new_user_data)
            
            # Коммит произойдет автоматически при выходе из `uow.atomic()`
            return persisted_user