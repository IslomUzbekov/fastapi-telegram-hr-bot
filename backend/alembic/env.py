from logging.config import fileConfig

from alembic import context
from app.core.settings import settings
from app.db import models  # noqa: F401  (нужно чтобы alembic видел модели)
from app.db.base import Base
from sqlalchemy import engine_from_config, pool

# Alembic Config object
config = context.config

# Подключаем логирование
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Указываем metadata для autogenerate
target_metadata = Base.metadata


def get_database_url() -> str:
    """
    Возвращает database URL из settings.
    """
    return settings.database_url


def run_migrations_offline() -> None:
    """
    Offline режим — без подключения к БД.
    """
    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Online режим — с подключением к БД.
    """

    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # чтобы alembic видел изменения типов
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
