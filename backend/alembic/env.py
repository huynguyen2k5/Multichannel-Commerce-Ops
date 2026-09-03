from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

from app.config import get_settings

# Model modules are imported so SQLModel metadata is populated before autogenerate runs.
# New modules should be added here only when they introduce persisted tables.
from app.modules.alerts import models as alert_models  # noqa: F401,E402
from app.modules.channels import models as channel_models  # noqa: F401,E402
from app.modules.ledger import models as ledger_models  # noqa: F401,E402
from app.modules.orders import models as order_models  # noqa: F401,E402
from app.modules.products import models as product_models  # noqa: F401,E402
from app.modules.reconciliation import models as reconciliation_models  # noqa: F401,E402

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def migration_url() -> str:
    settings = get_settings()
    return settings.migration_database_url or settings.database_url.replace(
        "postgresql+asyncpg://", "postgresql+psycopg://", 1
    )


def run_migrations_offline() -> None:
    context.configure(
        url=migration_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = migration_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
