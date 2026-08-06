import os
import tempfile
import unittest
from pathlib import Path

from app import create_app
from database import db
from helpers.report_service import generate_html_report
from models import Analysis, Project, User


class TestConfig:
    TESTING = True
    SECRET_KEY = "report-authorization-test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    MAIL_SUPPRESS_SEND = True
    SECURITY_HEADERS_ENABLED = True
    HSTS_ENABLED = False


class ReportAuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.temp_dir = tempfile.TemporaryDirectory()

        with self.app.app_context():
            db.drop_all()
            db.create_all()
            self.owner_id, self.other_user_id, self.analysis_id = self._seed_records()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()
        self.temp_dir.cleanup()

    def _seed_records(self):
        owner = User(
            username="report-owner",
            email="owner@example.com",
            email_verified=True,
        )
        owner.set_password("StrongPass123!")

        other = User(
            username="other-user",
            email="other@example.com",
            email_verified=True,
        )
        other.set_password("StrongPass123!")

        db.session.add_all([owner, other])
        db.session.flush()

        project = Project(
            project_id="project-report-test",
            project_name="Owner <Project>",
            original_filename="owner_project.py",
            stored_filename="owner_project.py",
            file_type="py",
            file_size=128,
            project_path=self.temp_dir.name,
            user_id=owner.id,
        )
        db.session.add(project)
        db.session.flush()

        analysis = Analysis(
            project_id=project.id,
            user_id=owner.id,
            filename="owner_project.py",
            overall_score=88.5,
            pylint_score=9.2,
            security_count=0,
            issues_count=2,
            total_files=1,
            total_lines=20,
            recommendations="Fix <unsafe> output",
            ai_summary="Summary <script>alert(1)</script>",
            status="Completed",
        )
        db.session.add(analysis)
        db.session.commit()

        return owner.id, other.id, analysis.id

    def _login_as(self, user_id):
        with self.client.session_transaction() as session:
            session["_user_id"] = str(user_id)
            session["_fresh"] = True

    def test_report_generator_creates_escaped_html_artifact(self):
        with self.app.app_context():
            project = Project.query.filter_by(user_id=self.owner_id).one()
            analysis = db.session.get(Analysis, self.analysis_id)

            previous_directory = os.getcwd()
            os.chdir(self.temp_dir.name)
            try:
                report_path = generate_html_report(project, analysis)
            finally:
                os.chdir(previous_directory)

            artifact = Path(self.temp_dir.name, report_path)
            self.assertTrue(artifact.is_file())
            html = artifact.read_text(encoding="utf-8")

        self.assertIn("Sentrix Analysis Report", html)
        self.assertIn("Owner &lt;Project&gt;", html)
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
        self.assertIn("Fix &lt;unsafe&gt; output", html)

    def test_owner_can_download_existing_report(self):
        report_file = Path(self.temp_dir.name, "owner-report.html")
        report_file.write_text("<html>owner report</html>", encoding="utf-8")

        with self.app.app_context():
            analysis = db.session.get(Analysis, self.analysis_id)
            analysis.report_path = str(report_file)
            db.session.commit()

        self._login_as(self.owner_id)
        response = self.client.get(
            f"/download_report/{self.analysis_id}",
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/html")
        self.assertIn("attachment", response.headers.get("Content-Disposition", ""))
        self.assertIn(b"owner report", response.data)

    def test_other_user_cannot_download_owners_report(self):
        report_file = Path(self.temp_dir.name, "private-report.html")
        report_file.write_text("private", encoding="utf-8")

        with self.app.app_context():
            analysis = db.session.get(Analysis, self.analysis_id)
            analysis.report_path = str(report_file)
            db.session.commit()

        self._login_as(self.other_user_id)
        response = self.client.get(
            f"/download_report/{self.analysis_id}",
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 404)
        self.assertNotIn(b"private", response.data)

    def test_other_user_cannot_view_owners_results(self):
        self._login_as(self.other_user_id)
        response = self.client.get(
            f"/results/{self.analysis_id}",
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/dashboard"))

    def test_missing_report_redirects_owner_to_results(self):
        with self.app.app_context():
            analysis = db.session.get(Analysis, self.analysis_id)
            analysis.report_path = str(Path(self.temp_dir.name, "missing.html"))
            db.session.commit()

        self._login_as(self.owner_id)
        response = self.client.get(
            f"/download_report/{self.analysis_id}",
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            response.headers["Location"].endswith(
                f"/results/{self.analysis_id}"
            )
        )


if __name__ == "__main__":
    unittest.main()
