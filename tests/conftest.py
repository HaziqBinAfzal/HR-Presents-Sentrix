import os

import pytest

from app import create_app
from database import db
from models import Analysis, Project, User


class TestConfig:
    TESTING = True
    SECRET_KEY = "sentrix-test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    MAIL_SUPPRESS_SEND = True
    MAIL_DEFAULT_SENDER = "tests@sentrix.local"
    SUPPORT_EMAIL = "support@sentrix.local"

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "tmp", "uploads")
    TEMP_FOLDER = os.path.join(UPLOAD_FOLDER, "temp")
    PROJECT_FOLDER = os.path.join(UPLOAD_FOLDER, "projects")
    REPORT_FOLDER = os.path.join(UPLOAD_FOLDER, "reports")
    CORRECTED_FOLDER = os.path.join(UPLOAD_FOLDER, "corrected")
    DIFF_FOLDER = os.path.join(UPLOAD_FOLDER, "diff")


@pytest.fixture()
def app():
    application = create_app(TestConfig)

    with application.app_context():
        db.drop_all()
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def users(app):
    with app.app_context():
        owner = User(username="owner", email="owner@example.com")
        owner.set_password("password123")
        outsider = User(username="outsider", email="outsider@example.com")
        outsider.set_password("password123")
        db.session.add_all([owner, outsider])
        db.session.commit()
        return owner.id, outsider.id


@pytest.fixture()
def analysis_record(app, users):
    owner_id, _ = users
    with app.app_context():
        project = Project(
            project_id="project-test-001",
            project_name="Sample Project",
            original_filename="sample.py",
            stored_filename="sample.py",
            file_type="py",
            file_size=128,
            project_path=TestConfig.PROJECT_FOLDER,
            user_id=owner_id,
        )
        db.session.add(project)
        db.session.flush()

        analysis = Analysis(
            project_id=project.id,
            user_id=owner_id,
            filename="sample.py",
            overall_score=82.5,
            pylint_score=8.4,
            security_count=1,
            complexity="Low",
            ai_summary="Summary",
            recommendations="Recommendation",
        )
        db.session.add(analysis)
        db.session.commit()
        return project.project_id, analysis.id


def login(client, email, password="password123"):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=False,
    )
