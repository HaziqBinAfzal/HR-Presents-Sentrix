import os
import subprocess
import sys
import unittest

from app import create_app
from database import db


class SecureTestConfig:
    TESTING = True
    SECRET_KEY = "production-security-test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    MAIL_SUPPRESS_SEND = True
    SECURITY_HEADERS_ENABLED = True
    HSTS_ENABLED = True
    HSTS_MAX_AGE = 31536000
    CONTENT_SECURITY_POLICY = "default-src 'self'; frame-ancestors 'none'"
    PERMISSIONS_POLICY = "camera=(), microphone=(), geolocation=()"
    REFERRER_POLICY = "strict-origin-when-cross-origin"


class NoHstsTestConfig(SecureTestConfig):
    HSTS_ENABLED = False


class HeadersDisabledTestConfig(SecureTestConfig):
    SECURITY_HEADERS_ENABLED = False


class ProductionSecurityTests(unittest.TestCase):
    def _make_client(self, config_class):
        app = create_app(config_class)
        self.addCleanup(self._dispose_app, app)
        return app.test_client()

    @staticmethod
    def _dispose_app(app):
        with app.app_context():
            db.session.remove()
            db.engine.dispose()

    @staticmethod
    def _production_environment(**overrides):
        environment = os.environ.copy()
        environment["PYTHON_DOTENV_DISABLED"] = "1"
        environment["APP_ENV"] = "production"
        environment.update(overrides)
        return environment

    def test_security_headers_are_applied(self):
        client = self._make_client(SecureTestConfig)
        response = client.get("/")

        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(response.headers["X-Frame-Options"], "DENY")
        self.assertEqual(
            response.headers["Referrer-Policy"],
            "strict-origin-when-cross-origin",
        )
        self.assertEqual(
            response.headers["Permissions-Policy"],
            "camera=(), microphone=(), geolocation=()",
        )
        self.assertEqual(
            response.headers["Content-Security-Policy"],
            "default-src 'self'; frame-ancestors 'none'",
        )
        self.assertEqual(
            response.headers["Strict-Transport-Security"],
            "max-age=31536000; includeSubDomains",
        )
        self.assertEqual(response.headers["Cross-Origin-Opener-Policy"], "same-origin")
        self.assertEqual(response.headers["X-Permitted-Cross-Domain-Policies"], "none")
        self.assertEqual(response.headers["Cache-Control"], "no-store")

    def test_hsts_is_omitted_when_disabled(self):
        client = self._make_client(NoHstsTestConfig)
        response = client.get("/")

        self.assertNotIn("Strict-Transport-Security", response.headers)
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")

    def test_all_security_headers_can_be_disabled_for_controlled_testing(self):
        client = self._make_client(HeadersDisabledTestConfig)
        response = client.get("/")

        for header in (
            "X-Content-Type-Options",
            "X-Frame-Options",
            "Referrer-Policy",
            "Permissions-Policy",
            "Content-Security-Policy",
            "Strict-Transport-Security",
        ):
            self.assertNotIn(header, response.headers)

    def test_production_requires_secret_key(self):
        environment = self._production_environment(SECRET_KEY="")

        result = subprocess.run(
            [sys.executable, "-c", "import config"],
            cwd=os.path.dirname(os.path.dirname(__file__)),
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SECRET_KEY must be set", result.stderr)

    def test_production_defaults_enable_https_controls(self):
        environment = self._production_environment(
            SECRET_KEY="ci-production-secret",
        )
        for variable in (
            "SESSION_COOKIE_SECURE",
            "REMEMBER_COOKIE_SECURE",
            "HSTS_ENABLED",
            "PREFERRED_URL_SCHEME",
        ):
            environment.pop(variable, None)

        command = (
            "from config import Config; "
            "assert Config.SESSION_COOKIE_SECURE is True; "
            "assert Config.REMEMBER_COOKIE_SECURE is True; "
            "assert Config.HSTS_ENABLED is True; "
            "assert Config.PREFERRED_URL_SCHEME == 'https'"
        )
        result = subprocess.run(
            [sys.executable, "-c", command],
            cwd=os.path.dirname(os.path.dirname(__file__)),
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
