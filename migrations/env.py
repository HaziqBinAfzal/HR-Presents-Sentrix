from logging.config import fileConfig

from alembic import context
from flask import current_app

config = context.config
fileConfig(config.config_file_name)

target_db = current_app.extensions["migrate"].db

def get_engine():
    try:
        return target_db.get_engine()
    except (TypeError, AttributeError):
        return target_db.engine


def get_engine_url():
    return str(get_engine().url).replace("%", "%%")

config.set_main_option("sqlalchemy.url", get_engine_url())
target_metadata = target_db.metadata


def run_migrations_offline():
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connection = get_engine().connect()
    try:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=connection.dialect.name == "sqlite",
        )
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
