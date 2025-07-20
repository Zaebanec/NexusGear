import asyncio
import sys
from decimal import Decimal
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.infrastructure.config import settings
from src.infrastructure.database.models import Category, Product


async def seed_database():
    print("Connecting to the database...")
    engine = create_async_engine(settings.db.url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    print("Seeding data...")
    async with session_factory() as session:
        async with session.begin():
            # --- Создаем Категории ---
            category1 = Category(name="Смартфоны")
            category2 = Category(name="Ноутбуки")
            category3 = Category(name="Аксессуары")
            session.add_all([category1, category2, category3])

            # --- НАЧАЛО ИСПРАВЛЕНИЯ ---
            # Принудительно отправляем INSERT'ы в БД и получаем ID для категорий
            await session.flush()
            # --- КОНЕЦ ИСПРАВЛЕНИЯ ---
            
            # Теперь мы гарантированно имеем category1.id, category2.id и т.д.
            
            products_to_add = [
                Product(
                    name="Nexus Prime X",
                    description="Флагманский смартфон с AI-камерой.",
                    price=Decimal("79990.99"),
                    category_id=category1.id, # Используем явный ID
                ),
                Product(
                    name="Nexus Vision",
                    description="Смартфон с безрамочным экраном.",
                    price=Decimal("54990.00"),
                    category_id=category1.id,
                ),
                Product(
                    name="GearBook Pro 16",
                    description="Мощный ноутбук для профессионалов.",
                    price=Decimal("149990.00"),
                    category_id=category2.id,
                ),
                Product(
                    name="GearBook Air",
                    description="Легкий и тонкий ноутбук для повседневных задач.",
                    price=Decimal("89990.50"),
                    category_id=category2.id,
                ),
                Product(
                    name="Nexus Buds 2",
                    description="Беспроводные наушники с шумоподавлением.",
                    price=Decimal("12990.00"),
                    category_id=category3.id,
                ),
            ]
            session.add_all(products_to_add)

    await engine.dispose()
    print("Database has been seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())