import os
import sys
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

# Добавляем корень проекта в sys.path, чтобы Alembic мог найти наши модули
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Наши кастомные импорты ---
from src.bot.core.config import settings
from src.bot.models.base import Base
# --- Конец кастомных импортов ---

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- Наша кастомная конфигурация ---
# Устанавливаем URL для подключения к БД из наших настроек
config.set_main_option("sqlalchemy.url", settings.database_url_asyncpg)

# Указываем Alembic на метаданные наших моделей для автогенерации
target_metadata = Base.metadata
# --- Конец кастомной конфигурации ---

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    connectable = create_async_engine(config.get_main_option("sqlalchemy.url"))
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

import asyncio

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())