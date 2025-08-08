# src/application/services/ai_consultant.py

import json
from typing import Dict, Any

from src.application.contracts.ai.ai_consultant import IAIConsultantService
from src.application.interfaces.repositories.product_repository import IProductRepository
from src.infrastructure.ai.gemini_client import GeminiClient

class AIConsultantService(IAIConsultantService):
    def __init__(
        self,
        gemini_client: GeminiClient,
        product_repo: IProductRepository,
    ):
        self._gemini_client = gemini_client
        self._product_repo = product_repo

    async def get_recommendation(self, user_query: str) -> Dict[str, Any]:
        products = await self._product_repo.get_all()
        if not products:
            return {
                "product_id": None,
                "explanation": "К сожалению, в данный момент товары отсутствуют."
            }

        # Формируем контекст для AI
        products_context = "\n".join(
            [f"ID: {p.id}, Имя: {p.name}, Описание: {p.description}, Цена: {p.price}" for p in products]
        )

        # Создаем промпт
        prompt = f"""
Ты — "AI-Сомелье Техники" в интернет-магазине. Твоя задача — помочь пользователю выбрать один, самый подходящий товар на основе его запроса.

Вот список доступных товаров:
--- НАЧАЛО СПИСКА ТОВАРОВ ---
{products_context}
--- КОНЕЦ СПИСКА ТОВАРОВ ---

Вот запрос пользователя:
--- НАЧАЛО ЗАПРОСА ---
{user_query}
--- КОНЕЦ ЗАПРОСА ---

Твои действия:
1. Внимательно проанализируй запрос пользователя и пойми его скрытые потребности.
2. Выбери из списка ОДИН, самый подходящий товар.
3. Напиши краткое (2-3 предложения), но убедительное объяснение, почему именно этот товар является лучшим выбором для пользователя. Обращайся к пользователю на "ты".
4. Верни ответ СТРОГО в формате JSON, без каких-либо других слов до или после.

Пример формата JSON:
{{
  "product_id": 123,
  "explanation": "Этот ноутбук идеально подойдет для твоих задач, потому что..."
}}
"""
        
        raw_response = await self._gemini_client.get_recommendation(prompt)
        
        try:
            # Убираем "мусор" вокруг JSON, если он есть
            json_response_str = raw_response.strip().replace("```json", "").replace("```", "")
            parsed_response = json.loads(json_response_str)
            return parsed_response
        except (json.JSONDecodeError, KeyError) as e:
            # Если AI вернул что-то не то, возвращаем ошибку
            return {
                "product_id": None,
                "explanation": "Извините, я не смог подобрать рекомендацию. Попробуйте переформулировать ваш запрос."
            }