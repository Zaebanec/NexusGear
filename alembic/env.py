import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# --- НАЧАЛО НАШЕЙ КОНФИГУРАЦИИ ---

# 1. Импортируем наш объект настроек и базовый класс моделей
#    Путь к 'base' должен существовать, мы создали его ранее.
from src.infrastructure.config import settings
from src.infrastructure.database.models.base import Base

# --- КОНЕЦ НАШЕЙ КОНФИГУРАЦИИ ---

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# --- НАЧАЛО НАШЕЙ КОНФИГУРАЦИИ ---

# 2. Устанавливаем URL для подключения к БД из нашего объекта настроек.
#    Это каноничный способ переопределить значение из alembic.ini.
config.set_main_option("sqlalchemy.url", settings.db.url)

# 3. Устанавливаем нашу декларативную базу как источник метаданных
#    для автогенерации миграций.
target_metadata = Base.metadata

# --- КОНЕЦ НАШЕЙ КОНФИГУРАЦИИ ---


# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
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
    """Run migrations in 'online' mode."""
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())