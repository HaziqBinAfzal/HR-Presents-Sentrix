"""Small compatibility migrations for existing Sentrix installations.

These additive migrations keep existing SQLite deployments working until the
repository adopts a complete Alembic migration history. They never drop or
rename user data.
"""

from sqlalchemy import inspect, text

from database import db


USER_COLUMNS = {
    "full_name": "VARCHAR(160)",
    "organization": "VARCHAR(160)",
    "bio": "TEXT",
    "role": "VARCHAR(80) DEFAULT 'Developer' NOT NULL",
    "workspace": "VARCHAR(160) DEFAULT 'Personal Workspace' NOT NULL",
    "email_verified": "BOOLEAN DEFAULT 0 NOT NULL",
    "email_verified_at": "DATETIME",
    "verification_sent_at": "DATETIME",
    "failed_login_attempts": "INTEGER DEFAULT 0 NOT NULL",
    "locked_until": "DATETIME",
    "last_login_at": "DATETIME",
    "last_login_ip": "VARCHAR(64)",
    "password_changed_at": "DATETIME",
    "two_factor_enabled": "BOOLEAN DEFAULT 0 NOT NULL",
    "two_factor_secret": "VARCHAR(255)",
    "backup_codes_hash": "TEXT",
}


def apply_additive_schema_compatibility():
    """Add missing user columns to legacy databases without data loss.

    New authentication tables are created by ``db.create_all()`` before this
    function runs. This helper only handles columns that SQLite cannot add via
    SQLAlchemy's normal create-all behavior.
    """
    inspector = inspect(db.engine)
    if "users" not in inspector.get_table_names():
        return

    existing_columns = {
        column["name"] for column in inspector.get_columns("users")
    }

    with db.engine.begin() as connection:
        for column_name, column_type in USER_COLUMNS.items():
            if column_name in existing_columns:
                continue
            connection.execute(
                text(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}")
            )
