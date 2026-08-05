import unittest
from unittest.mock import patch

from app import create_app
from database import db
from models import User


class TestConfig:
    TESTING = True
    SECRET_KEY = "sentrix-ci-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    MAIL_SUPPRESS_SEND = True
    UPLOAD_FOLDER = "uploads"
    PROJECT_FOLDER = "uploads/projects"


class ApplicationFlowTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.context = self.app.app_context()
        self.context.push()
        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def test_public_pages_load(self):
        for path in ("/", "/about", "/login", "/register", "/contact", "/reviews"):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)

    def test_protected_pages_redirect_anonymous_users(self):
        for path in ("/dashboard", "/settings", "/profile", "/history", "/upload"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 302)
                self.assertIn("/login", response.headers["Location"])

    def test_register_login_logout_flow(self):
        register = self.client.post(
            "/register",
            data={
                "username": "ci-user",
                "email": "ci-user@example.com",
                "password": "StrongPassword123!",
                "confirm_password": "StrongPassword123!",
            },
            follow_redirects=False,
        )
        self.assertEqual(register.status_code, 302)
        user = User.query.filter_by(email="ci-user@example.com").one()
        self.assertTrue(user.check_password("StrongPassword123!"))

        login = self.client.post(
            "/login",
            data={"email": "ci-user@example.com", "password": "StrongPassword123!"},
            follow_redirects=False,
        )
        self.assertEqual(login.status_code, 302)
        self.assertIn("/dashboard", login.headers["Location"])

        dashboard = self.client.get("/dashboard")
        self.assertEqual(dashboard.status_code, 200)

        logout = self.client.get("/logout", follow_redirects=False)
        self.assertEqual(logout.status_code, 302)
        self.assertIn("/login", logout.headers["Location"])

    def test_duplicate_registration_is_rejected(self):
        user = User(username="existing", email="existing@example.com")
        user.set_password("StrongPassword123!")
        db.session.add(user)
        db.session.commit()

        response = self.client.post(
            "/register",
            data={
                "username": "existing",
                "email": "existing@example.com",
                "password": "StrongPassword123!",
                "confirm_password": "StrongPassword123!",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.query.count(), 1)

    def test_contact_form_uses_mail_extension(self):
        with patch("analyzer.routes.main.mail.send") as send:
            response = self.client.post(
                "/contact",
                data={
                    "name": "CI User",
                    "email": "ci@example.com",
                    "subject": "Automated test",
                    "message": "This is a valid contact form message.",
                },
                follow_redirects=False,
            )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/contact", response.headers["Location"])
        send.assert_called_once()

    def test_error_pages_render(self):
        self.assertEqual(self.client.get("/missing-page").status_code, 404)
        self.assertEqual(self.client.get("/forbidden").status_code, 403)


if __name__ == "__main__":
    unittest.main()
