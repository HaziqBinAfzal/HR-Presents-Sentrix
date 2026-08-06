import sqlite3
import tempfile
import unittest
from pathlib import Path

from sqlalchemy import inspect

from app import create_app
from database import db
from models import User


class DatabaseCompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.database_path = Path(self.temp_dir.name) / "sentrix-test.db"

    def _config(self):
        database_uri = f"sqlite:///{self.database_path}"

        class TestConfig:
            TESTING = True
            SECRET_KEY = "database-compatibility-test-secret"
            SQLALCHEMY_DATABASE_URI = database_uri
            SQLALCHEMY_TRACK_MODIFICATIONS = False
            WTF_CSRF_ENABLED = False
            MAIL_SUPPRESS_SEND = True
            SECURITY_HEADERS_ENABLED = False
            HSTS_ENABLED = False

        return TestConfig

    def _create_app(self):
        app = create_app(self._config())
        self.addCleanup(self._dispose_app, app)
        return app

    @staticmethod
    def _dispose_app(app):
        with app.app_context():
            db.session.remove()
            db.engine.dispose()

    def test_fresh_database_contains_current_schema(self):
        app = self._create_app()

        with app.app_context():
            inspector = inspect(db.engine)
            tables = set(inspector.get_table_names())
            self.assertTrue(
                {"users", "projects", "analyses", "reviews", "user_settings"}
                .issubset(tables)
            )

            user_columns = {column["name"] for column in inspector.get_columns("users")}
            expected_columns = {
                "id",
                "username",
                "email",
                "password_hash",
                "full_name",
                "organization",
                "bio",
                "role",
                "workspace",
                "profile_picture",
                "created_at",
            }
            self.assertTrue(expected_columns.issubset(user_columns))
            self.assertNotIn("email_verified", user_columns)
            self.assertNotIn("email_verified_at", user_columns)

    def test_legacy_user_is_preserved_when_current_tables_are_created(self):
        connection = sqlite3.connect(self.database_path)
        try:
            connection.execute(
                """
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    username VARCHAR(80) NOT NULL UNIQUE,
                    email VARCHAR(120) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    full_name VARCHAR(160),
                    organization VARCHAR(160),
                    bio TEXT,
                    role VARCHAR(80) NOT NULL DEFAULT 'user',
                    workspace VARCHAR(160) NOT NULL DEFAULT 'personal',
                    profile_picture VARCHAR(255) DEFAULT 'default.png',
                    created_at DATETIME NOT NULL
                )
                """
            )
            connection.execute(
                """
                INSERT INTO users (
                    id, username, email, password_hash, role, workspace,
                    profile_picture, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    7,
                    "legacy-user",
                    "legacy@example.com",
                    "legacy-password-hash",
                    "user",
                    "personal",
                    "default.png",
                    "2026-01-01 00:00:00",
                ),
            )
            connection.commit()
        finally:
            connection.close()

        app = self._create_app()

        with app.app_context():
            inspector = inspect(db.engine)
            tables = set(inspector.get_table_names())
            self.assertTrue(
                {"users", "projects", "analyses", "reviews", "user_settings"}
                .issubset(tables)
            )

            user = db.session.get(User, 7)
            self.assertIsNotNone(user)
            self.assertEqual(user.username, "legacy-user")
            self.assertEqual(user.email, "legacy@example.com")

    def test_schema_initialization_is_idempotent(self):
        first_app = self._create_app()
        self._dispose_app(first_app)

        second_app = create_app(self._config())
        self.addCleanup(self._dispose_app, second_app)

        with second_app.app_context():
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            self.assertEqual(tables.count("users"), 1)
            self.assertEqual(tables.count("projects"), 1)
            self.assertEqual(tables.count("analyses"), 1)
            self.assertEqual(tables.count("reviews"), 1)
            self.assertEqual(tables.count("user_settings"), 1)

            user_columns = [column["name"] for column in inspector.get_columns("users")]
            self.assertEqual(len(user_columns), len(set(user_columns)))
            self.assertNotIn("email_verified", user_columns)
            self.assertNotIn("email_verified_at", user_columns)


if __name__ == "__main__":
    unittest.main()
