# tests/application/services/test_order_service.py

import pytest
from unittest.mock import AsyncMock, MagicMock
from decimal import Decimal

from src.application.services.order_service import OrderService
from src.domain.entities.cart_item import CartItem
from src.domain.entities.product import Product
from src.domain.entities.order import Order

@pytest.fixture
def mock_uow():
    """Фикстура для мока Unit of Work."""
    return AsyncMock()

@pytest.fixture
def mock_cart_repo():
    """Фикстура для мока репозитория корзины."""
    return AsyncMock()

@pytest.fixture
def order_service(mock_uow, mock_cart_repo):
    """Фикстура для создания экземпляра OrderService с моками."""
    return OrderService(uow=mock_uow, cart_repository=mock_cart_repo)

@pytest.mark.asyncio
async def test_create_order_successfully(order_service, mock_uow, mock_cart_repo):
    """
    Тест: успешное создание заказа.
    Проверяет, что сервис корректно создает заказ на основе содержимого корзины,
    сохраняет его в БД через UoW и очищает корзину.
    """
    # 1. Arrange (Подготовка)
    user_id = 12345
    
    # Моделируем товары и корзину
    product1 = Product(id=1, name="Test Product 1", price=Decimal("100.00"), category_id=1)
    product2 = Product(id=2, name="Test Product 2", price=Decimal("50.50"), category_id=1)
    
    cart_items = [
        CartItem(product=product1, quantity=2), # 2 * 100.00 = 200.00
        CartItem(product=product2, quantity=1), # 1 * 50.50 = 50.50
    ]
    # Ожидаемая общая сумма: 250.50
    
    # Настраиваем моки
    mock_cart_repo.get_cart_items.return_value = cart_items
    
    # 2. Act (Действие)
    created_order = await order_service.create_order(user_id)

    # 3. Assert (Проверка)
    
    # Проверяем, что UoW был использован для коммита
    mock_uow.commit.assert_awaited_once()
    
    # Проверяем, что репозиторий заказов был вызван для добавления заказа
    mock_uow.orders.add.assert_called_once()
    
    # Проверяем, что корзина была очищена для данного пользователя
    mock_cart_repo.clear_cart.assert_awaited_once_with(user_id)
    
    # Проверяем детали созданного заказа
    # mock_uow.orders.add.call_args.args[0] получает первый аргумент, 
    # с которым был вызван метод add()
    added_order: Order = mock_uow.orders.add.call_args.args[0]
    
    assert isinstance(added_order, Order)
    assert added_order.user_id == user_id
    assert len(added_order.items) == 2
    assert added_order.total_amount == Decimal("250.50")
    
    # Проверяем корректность элементов заказа
    assert added_order.items[0].product_id == 1
    assert added_order.items[0].quantity == 2
    assert added_order.items[0].price == Decimal("100.00")
    
    assert added_order.items[1].product_id == 2
    assert added_order.items[1].quantity == 1
    assert added_order.items[1].price == Decimal("50.50")
    
    assert created_order is not None
    assert created_order.id == added_order.id