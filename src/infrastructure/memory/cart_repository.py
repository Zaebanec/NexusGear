from collections import defaultdict
from src.application.contracts.cart.cart_repository import ICartRepository
from src.domain.entities.cart_item import CartItem

class InMemoryCartRepository(ICartRepository):
    """
    In-memory реализация репозитория корзины.
    """
    def __init__(self):
        self._carts: dict[int, list[CartItem]] = defaultdict(list)

    async def get_by_user_id(self, user_id: int) -> list[CartItem]:
        return self._carts.get(user_id, []).copy()

    async def clear_by_user_id(self, user_id: int) -> None:
        if user_id in self._carts:
            del self._carts[user_id]
    
    # --- НАЧАЛО ИЗМЕНЕНИЙ ---
    async def add_item(self, user_id: int, item: CartItem) -> None:
        """Добавляет товар в корзину или увеличивает его количество."""
        cart = self._carts[user_id]
        # Проверяем, есть ли уже такой товар в корзине
        for existing_item in cart:
            if existing_item.product_id == item.product_id:
                existing_item.quantity += item.quantity
                return # Выходим, если товар обновлен
        
        # Если товара нет, добавляем его
        cart.append(item)
    # --- КОНЕЦ ИЗМЕНЕНИЙ ---