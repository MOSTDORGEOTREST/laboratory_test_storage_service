from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from alembic import context
from database import Base
from sqlalchemy import pool
from alembic.config import Config
import asyncio
import os
from config import configs

# Определите метаданные для ваших моделей
target_metadata = Base.metadata

# Настройка подключения к базе данных
config = context.config
config.set_main_option("sqlalchemy.url", configs.database_url)

def run_migrations_offline():
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

async def run_migrations_online():
    """Run migrations in 'online' mode."""
    config = context.config
    url = config.get_main_option("sqlalchemy.url")
    connectable = create_async_engine(url, poolclass=pool.NullPool)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

def do_run_migrations(connection):
    """Run migrations with the provided connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

# Get the Alembic configuration
config = Config("alembic.ini")

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())