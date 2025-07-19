from abc import ABC, abstractmethod
from src.domain.entities.cart_item import CartItem

class ICartRepository(ABC):
    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> list[CartItem]:
        raise NotImplementedError

    @abstractmethod
    async def clear_by_user_id(self, user_id: int) -> None:
        raise NotImplementedError