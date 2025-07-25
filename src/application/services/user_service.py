# src/application/services/user_service.py - ФИНАЛЬНАЯ ИСПРАВЛЕННАЯ ВЕРСИЯ

from src.application.contracts.persistence.uow import IUnitOfWork
from src.domain.entities.user import User as DomainUser

class UserService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def register_user_if_not_exists(
        self,
        telegram_id: int,
        full_name: str,
        username: str | None,
    ) -> DomainUser:
        # Объявляем переменную для результата заранее
        user_to_return: DomainUser

        # --- КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ: Логика `return` вынесена из блока `with` ---
        async with self.uow.atomic():
            existing_user = await self.uow.users.get_by_telegram_id(telegram_id)
            if existing_user:
                # Мы не выходим из функции, а просто сохраняем результат
                user_to_return = existing_user
            else:
                new_user_data = DomainUser(
                    id=0,
                    telegram_id=telegram_id,
                    full_name=full_name,
                    username=username,
                )
                # Репозиторий вернет нам сущность с ID, мы сохраняем ее
                persisted_user = await self.uow.users.add(new_user_data)
                user_to_return = persisted_user
        
        # Блок `with self.uow.atomic()` завершился штатно.
        # SQLAlchemy выполнил COMMIT.
        # Теперь мы можем безопасно вернуть результат.
        return user_to_return