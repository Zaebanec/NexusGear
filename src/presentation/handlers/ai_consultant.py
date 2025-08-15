# src/presentation/handlers/ai_consultant.py - НОВАЯ ВЕРСИЯ

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, WebAppInfo # <-- 1. Импортируем WebAppInfo
from dishka import AsyncContainer, Scope
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ChatAction

from src.application.services.ai_consultant import AIConsultantService
from src.application.services.catalog import ProductService
# from src.presentation.handlers.catalog import AddProductCallbackFactory <-- 2. УДАЛЯЕМ НЕНУЖНЫЙ ИМПОРТ
from src.infrastructure.config import settings # <-- 3. Импортируем настройки для URL

ai_router = Router()

class AIConsultation(StatesGroup):
    waiting_for_query = State()

@ai_router.message(F.text == "🤖 AI-Консультант")
async def start_consultation(message: Message, state: FSMContext):
    await message.answer(
        "Я ваш AI-помощник! 🤖\n\n"
        "Опишите своими словами, для каких задач вам нужен товар, и я подберу "
        "лучший вариант из нашего каталога.\n\n"
        "Например: <i>'Я ищу ноутбук для работы с графикой, важен хороший экран и мощность.'</i>"
    )
    await state.set_state(AIConsultation.waiting_for_query)

@ai_router.message(AIConsultation.waiting_for_query)
async def process_query(message: Message, state: FSMContext, dishka_container: AsyncContainer):
    await message.chat.do(ChatAction.TYPING)
    
    if not message.text:
        await message.answer("Пожалуйста, отправьте текстовое сообщение с запросом.")
        return
    async with dishka_container(scope=Scope.REQUEST) as request_container:
        ai_service = await request_container.get(AIConsultantService)
        product_service = await request_container.get(ProductService)
        
        recommendation = await ai_service.get_recommendation(message.text)
        
        product_id = recommendation.get("product_id")
        explanation = str(recommendation.get("explanation") or "")

        if product_id:
            product = await product_service.get_by_id(product_id)
            if product:
                card = (
                    f"<b>{product.name}</b>\n"
                    f"<i>Цена: {product.price} руб.</i>\n\n"
                    f"{product.description}"
                )
                
                # --- 4. КЛЮЧЕВОЕ ИЗМЕНЕНИЕ: Создаем кнопку-ссылку в Web App ---
                builder = InlineKeyboardBuilder()
                # Формируем "глубокую ссылку" на страницу продукта
                web_app_url = f"{settings.app.base_url}/products/{product.id}"
                builder.button(
                    text="🛒 Посмотреть в магазине",
                    web_app=WebAppInfo(url=web_app_url)
                )
                # --- КОНЕЦ ИЗМЕНЕНИЯ ---

                await message.answer(card, reply_markup=builder.as_markup())
                await message.answer(f"<b>🤖 Моя рекомендация:</b>\n\n{explanation}")
            else:
                await message.answer("Произошла ошибка: рекомендованный товар не найден в базе.")
        else:
            await message.answer(explanation)

    await state.clear()