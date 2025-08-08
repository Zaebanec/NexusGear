# src/application/contracts/ai/ai_consultant.py

from abc import ABC, abstractmethod

# Можно определить DTO для более строгого контракта, но для MVP сойдет и dict
from typing import Dict, Any

class IAIConsultantService(ABC):
    @abstractmethod
    async def get_recommendation(self, user_query: str) -> Dict[str, Any]:
        """
        Получает текстовый запрос пользователя, возвращает рекомендацию.
        """
        raise NotImplementedError