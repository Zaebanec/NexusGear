# src/infrastructure/ai/gemini_client.py

import google.generativeai as genai

from src.infrastructure.config import Settings


class GeminiClient:
    """
    Клиент для взаимодействия с Google Gemini API.
    Инкапсулирует настройку и вызов модели.
    """
    def __init__(self, settings: Settings):
        genai.configure(api_key=settings.gemini.api_key.get_secret_value())
        # Используем модель gemini-1.5-flash - она быстрая и экономичная
        self._model = genai.GenerativeModel('gemini-1.5-flash')

    async def get_recommendation(self, prompt: str) -> str:
        """
        Отправляет промпт в Gemini и возвращает текстовый ответ.
        """
        # Используем асинхронный метод generate_content_async
        response = await self._model.generate_content_async(prompt)
        return response.text