# src/infrastructure/telegram/notifier.py
from __future__ import annotations
from typing import Optional
from aiogram import Bot
from src.application.contracts.notifications.notifier import INotifier
from src.domain.entities.order import Order

class TelegramNotifier(INotifier):
    def __init__(self, bot: Bot):
        self._bot = bot

    async def notify_order_created(
        self,
        telegram_id: int,
        order: Order,
        full_name: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
    ) -> None:
        parts = [
            f"✅ Ваш заказ №{order.id} успешно создан!",
            "",
        ]
        if full_name:
            parts.append(f"<b>Получатель:</b> {full_name}")
        if phone:
            parts.append(f"<b>Телефон:</b> {phone}")
        if address:
            parts.append(f"<b>Адрес:</b> {address}")
        parts.append("")
        parts.append("В ближайшее время с вами свяжется наш менеджер.")

        text = "\n".join(parts)
        await self._bot.send_message(chat_id=telegram_id, text=text, parse_mode="HTML")
