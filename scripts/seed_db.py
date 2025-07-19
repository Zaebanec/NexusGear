import asyncio
import sys
from decimal import Decimal
from pathlib import Path

# --- Хак для корректного импорта из `src` ---
# Добавляем корневую директорию проекта в PYTHONPATH,
# чтобы скрипт мог найти модуль `src`.
sys.path.append(str(Path(__file__).parent.parent))
# ---------------------------------------------

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.infrastructure.config import settings
from src.infrastructure.database.models import Category, Product


async def seed_database():
    """
    Основная функция для наполнения базы данных тестовыми данными.
    """
    print("Connecting to the database...")
    engine = create_async_engine(settings.db.url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    print("Seeding data...")
    async with session_factory() as session:
        async with session.begin():  # Начинаем транзакцию
            # --- Создаем Категории ---
            category1 = Category(name="Смартфоны")
            category2 = Category(name="Ноутбуки")
            category3 = Category(name="Аксессуары")

            session.add_all([category1, category2, category3])
            
            # --- Создаем Товары ---
            products_to_add = [
                Product(
                    name="Nexus Prime X",
                    description="Флагманский смартфон с AI-камерой.",
                    price=Decimal("79990.99"),
                    category=category1,
                ),
                Product(
                    name="Nexus Vision",
                    description="Смартфон с безрамочным экраном.",
                    price=Decimal("54990.00"),
                    category=category1,
                ),
                Product(
                    name="GearBook Pro 16",
                    description="Мощный ноутбук для профессионалов.",
                    price=Decimal("149990.00"),
                    category=category2,
                ),
                Product(
                    name="GearBook Air",
                    description="Легкий и тонкий ноутбук для повседневных задач.",
                    price=Decimal("89990.50"),
                    category=category2,
                ),
                Product(
                    name="Nexus Buds 2",
                    description="Беспроводные наушники с шумоподавлением.",
                    price=Decimal("12990.00"),
                    category=category3,
                ),
            ]
            session.add_all(products_to_add)

    await engine.dispose()  # Закрываем все соединения
    print("Database has been seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())