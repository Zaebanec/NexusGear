from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from .config import settings

# Создаем асинхронный движок SQLAlchemy
engine = create_async_engine(settings.database_url_asyncpg)

# Создаем фабрику асинхронных сессий
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)