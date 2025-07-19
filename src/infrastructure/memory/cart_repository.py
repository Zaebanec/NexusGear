from collections import defaultdict
from src.application.contracts.cart.cart_repository import ICartRepository
from src.domain.entities.cart_item import CartItem

class InMemoryCartRepository(ICartRepository):
    """
    In-memory реализация репозитория корзины.
    Хранит данные в словаре. Подходит для разработки и тестов.
    ПРИМЕЧАНИЕ: Данные будут теряться при перезапуске приложения.
    """
    def __init__(self):
        # user_id -> list[CartItem]
        self._carts: dict[int, list[CartItem]] = defaultdict(list)

    async def get_by_user_id(self, user_id: int) -> list[CartItem]:
        # Возвращаем копию, чтобы избежать случайных мутаций извне
        return self._carts.get(user_id, []).copy()

    async def clear_by_user_id(self, user_id: int) -> None:
        if user_id in self._carts:
            del self._carts[user_id]
    
    # Примечание: методы для добавления/удаления товаров в корзину
    # будут реализованы на следующих шагах.