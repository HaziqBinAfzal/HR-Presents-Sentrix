"""Create a safe SQLite backup and print a read-only schema audit.

This utility does not stamp, migrate, or modify the source database.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlparse

from dotenv import load_dotenv


EXPECTED_TABLES = {
    "users",
    "projects",
    "analyses",
    "reviews",
    "user_settings",
}


def resolve_sqlite_path(database_url: str, project_root: Path) -> Path:
    parsed = urlparse(database_url)
    if parsed.scheme != "sqlite":
        raise ValueError(
            "This preflight utility currently supports SQLite only. "
            f"Configured scheme: {parsed.scheme or 'unknown'}"
        )

    raw_path = unquote(parsed.path)
    if database_url.startswith("sqlite:////"):
        return Path(raw_path).resolve()
    if database_url.startswith("sqlite:///"):
        return (project_root / raw_path.lstrip("/")).resolve()
    raise ValueError("Unsupported SQLite URL format.")


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Back up and inspect the active Sentrix SQLite database safely."
    )
    parser.add_argument(
        "--database-url",
        help="Override DATABASE_URL for this audit.",
    )
    parser.add_argument(
        "--backup-dir",
        default="backups/database-preflight",
        help="Directory for timestamped database backups.",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root / ".env")

    database_url = args.database_url or os.getenv("DATABASE_URL")
    if not database_url:
        database_url = f"sqlite:///{project_root / 'instance' / 'database.db'}"

    try:
        database_path = resolve_sqlite_path(database_url, project_root)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"Database URL: {database_url}")
    print(f"Resolved path: {database_path}")

    if not database_path.is_file():
        print("ERROR: Database file does not exist.", file=sys.stderr)
        return 3

    backup_dir = Path(args.backup_dir)
    if not backup_dir.is_absolute():
        backup_dir = project_root / backup_dir
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_path = backup_dir / f"{database_path.stem}-{timestamp}.sqlite3"
    shutil.copy2(database_path, backup_path)

    print(f"Backup created: {backup_path}")
    print(f"Backup size: {backup_path.stat().st_size} bytes")

    connection = sqlite3.connect(f"file:{database_path}?mode=ro", uri=True)
    try:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        print(f"Integrity check: {integrity}")

        tables = [
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
        ]

        print("Tables:")
        for table in tables:
            count = connection.execute(
                f"SELECT COUNT(*) FROM {quote_identifier(table)}"
            ).fetchone()[0]
            columns = [
                row[1]
                for row in connection.execute(
                    f"PRAGMA table_info({quote_identifier(table)})"
                )
            ]
            print(f"  - {table}: {count} rows")
            print(f"    columns: {', '.join(columns)}")

        missing = sorted(EXPECTED_TABLES.difference(tables))
        print(f"Missing expected tables: {', '.join(missing) if missing else 'none'}")

        if "alembic_version" in tables:
            revisions = [
                row[0]
                for row in connection.execute(
                    "SELECT version_num FROM alembic_version"
                )
            ]
            print(f"Alembic revision: {', '.join(revisions) if revisions else 'empty'}")
        else:
            print("Alembic revision: not stamped")
    finally:
        connection.close()

    print("Source database was opened read-only and was not modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
