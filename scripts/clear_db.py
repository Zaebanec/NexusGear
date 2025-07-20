import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.infrastructure.config import settings
from src.infrastructure.database.models import Base


async def clear_database():
    print("Connecting to the database to clear it...")
    engine = create_async_engine(settings.db.url)
    
    async with engine.begin() as conn:
        print("Dropping all tables...")
        # Удаляем все таблицы, которые унаследованы от Base
        await conn.run_sync(Base.metadata.drop_all)
        print("Recreating all tables...")
        # Создаем их заново
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()
    print("Database has been cleared and recreated successfully!")


if __name__ == "__main__":
    asyncio.run(clear_database())