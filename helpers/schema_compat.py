"""Small compatibility migrations for existing Sentrix installations.

These additive migrations keep existing SQLite deployments working until the
repository adopts a complete Alembic migration history. They never drop or
rename user data.
"""

from sqlalchemy import inspect, text

from database import db


USER_PROFILE_COLUMNS = {
    "full_name": "VARCHAR(160)",
    "organization": "VARCHAR(160)",
    "bio": "TEXT",
    "role": "VARCHAR(80) DEFAULT 'Developer' NOT NULL",
    "workspace": "VARCHAR(160) DEFAULT 'Personal Workspace' NOT NULL",
}


def apply_additive_schema_compatibility():
    """Add missing profile columns to legacy databases without data loss."""
    inspector = inspect(db.engine)
    if "users" not in inspector.get_table_names():
        return

    existing_columns = {
        column["name"] for column in inspector.get_columns("users")
    }

    with db.engine.begin() as connection:
        for column_name, column_type in USER_PROFILE_COLUMNS.items():
            if column_name in existing_columns:
                continue
            connection.execute(
                text(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}")
            )
