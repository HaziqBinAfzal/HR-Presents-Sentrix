import unittest

from app import create_app
from database import db
from helpers.email_verification import generate_email_verification_token
from models import User


class TestConfig:
    TESTING = True
    SECRET_KEY = "email-verification-test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    MAIL_SUPPRESS_SEND = True
    MAIL_DEFAULT_SENDER = "tests@sentrix.local"
    EMAIL_VERIFICATION_MAX_AGE = 3600
    SECURITY_HEADERS_ENABLED = True
    HSTS_ENABLED = False


class EmailVerificationFlowTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.drop_all()
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def _create_user(self, *, verified=False):
        with self.app.app_context():
            user = User(
                username="verification-user",
                email="verification@example.com",
                email_verified=verified,
            )
            user.set_password("StrongPass123!")
            if verified:
                user.mark_email_verified()
            db.session.add(user)
            db.session.commit()
            return user.id

    def test_registration_creates_unverified_user(self):
        response = self.client.post(
            "/register",
            data={
                "username": "new-user",
                "email": "New.User@Example.com",
                "password": "StrongPass123!",
                "confirm_password": "StrongPass123!",
            },
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/verification-pending", response.headers["Location"])

        with self.app.app_context():
            user = User.query.filter_by(email="new.user@example.com").one()
            self.assertFalse(user.email_verified)
            self.assertIsNone(user.email_verified_at)
            self.assertTrue(user.check_password("StrongPass123!"))

    def test_unverified_user_cannot_log_in(self):
        self._create_user(verified=False)

        response = self.client.post(
            "/login",
            data={
                "email": "verification@example.com",
                "password": "StrongPass123!",
            },
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/verification-pending", response.headers["Location"])

        with self.client.session_transaction() as session:
            self.assertNotIn("_user_id", session)

    def test_valid_token_marks_email_verified(self):
        user_id = self._create_user(verified=False)

        with self.app.app_context():
            user = db.session.get(User, user_id)
            token = generate_email_verification_token(user)

        response = self.client.get(
            f"/verify-email/{token}",
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/login"))

        with self.app.app_context():
            user = db.session.get(User, user_id)
            self.assertTrue(user.email_verified)
            self.assertIsNotNone(user.email_verified_at)

    def test_token_is_invalid_after_email_change(self):
        user_id = self._create_user(verified=False)

        with self.app.app_context():
            user = db.session.get(User, user_id)
            token = generate_email_verification_token(user)
            user.email = "changed@example.com"
            db.session.commit()

        response = self.client.get(
            f"/verify-email/{token}",
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/verification-pending", response.headers["Location"])

        with self.app.app_context():
            user = db.session.get(User, user_id)
            self.assertFalse(user.email_verified)

    def test_resend_response_does_not_reveal_account_state(self):
        unknown = self.client.post(
            "/verification/resend",
            data={"email": "unknown@example.com"},
            follow_redirects=True,
        )
        self.assertEqual(unknown.status_code, 200)
        self.assertIn(
            b"If an unverified account exists with that email",
            unknown.data,
        )

        self._create_user(verified=False)
        existing = self.client.post(
            "/verification/resend",
            data={"email": "verification@example.com"},
            follow_redirects=True,
        )
        self.assertEqual(existing.status_code, 200)
        self.assertIn(
            b"If an unverified account exists with that email",
            existing.data,
        )

    def test_verified_user_can_log_in(self):
        self._create_user(verified=True)

        response = self.client.post(
            "/login",
            data={
                "email": "verification@example.com",
                "password": "StrongPass123!",
            },
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/dashboard"))

        with self.client.session_transaction() as session:
            self.assertIn("_user_id", session)


if __name__ == "__main__":
    unittest.main()
