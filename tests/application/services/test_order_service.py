# tests/application/services/test_order_service.py - ФИНАЛЬНАЯ СИНХРОНИЗИРОВАННАЯ ВЕРСИЯ

import pytest
from unittest.mock import AsyncMock, MagicMock
from decimal import Decimal

from src.application.services.order_service import OrderService
from src.domain.entities.order import Order
from src.domain.entities.user import User
from src.domain.entities.cart_item import CartItem # Импортируем для использования в spec

@pytest.fixture
def mock_uow():
    """
    Фикстура для мока Unit of Work.
    Предоставляет моки для всех необходимых вложенных репозиториев.
    """
    uow = AsyncMock()
    uow.orders = AsyncMock()
    uow.users = AsyncMock()
    return uow

@pytest.fixture
def mock_cart_repo():
    """Фикстура для мока репозитория корзины."""
    return AsyncMock()

@pytest.fixture
def order_service(mock_uow, mock_cart_repo):
    """Фикстура для создания экземпляра OrderService с моками."""
    return OrderService(uow=mock_uow, cart_repo=mock_cart_repo)

@pytest.mark.asyncio
async def test_create_order_successfully(order_service, mock_uow, mock_cart_repo):
    """
    Тест: успешное создание заказа с использованием Unit of Work.
    Полностью синхронизирован с финальной версией OrderService.
    """
    # 1. Arrange (Подготовка)
    telegram_id = 12345
    internal_user_id = 999

    # Моделируем пользователя, которого вернет uow.users.get_by_telegram_id
    mock_user = User(
        id=internal_user_id,
        telegram_id=telegram_id,
        full_name="Test User",
        username=None
    )
    mock_uow.users.get_by_telegram_id.return_value = mock_user

    # Моделируем "умные" элементы корзины, которые ведут себя как настоящие
    item1 = MagicMock(spec=CartItem)
    item1.product_id = 1
    item1.price = Decimal("100.00")
    item1.quantity = 2

    item2 = MagicMock(spec=CartItem)
    item2.product_id = 2
    item2.price = Decimal("50.50")
    item2.quantity = 1

    cart_items_from_repo = [item1, item2]
    mock_cart_repo.get_by_user_id.return_value = cart_items_from_repo
    
    # 2. Act (Действие)
    created_order = await order_service.create_order(telegram_id)

    # 3. Assert (Проверка)
    
    # Проверяем, что сервис выполнил все необходимые вызовы
    mock_uow.users.get_by_telegram_id.assert_awaited_once_with(telegram_id)
    mock_cart_repo.get_by_user_id.assert_awaited_once_with(telegram_id)
    mock_uow.orders.create.assert_called_once()
    mock_cart_repo.clear_by_user_id.assert_awaited_once_with(telegram_id)
    
    # Проверяем детали сущности, переданной в репозиторий
    added_order_entity: Order = mock_uow.orders.create.call_args.args[0]
    
    assert isinstance(added_order_entity, Order)
    assert added_order_entity.user_id == internal_user_id
    assert added_order_entity.total_amount == Decimal("250.50")
    
    # Проверяем, что сервис вернул созданную сущность
    assert created_order is added_order_entity