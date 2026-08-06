import os
import tempfile
import unittest
from unittest.mock import patch

from app import create_app
from background_models import AnalysisJob
from database import db
from helpers.background_analysis import (
    claim_next_job,
    enqueue_analysis,
    fail_job,
    process_job,
)
from models import Analysis, Project, User


class BackgroundAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        database_path = os.path.join(self.temp_dir.name, "jobs.db")

        class TestConfig:
            TESTING = True
            SECRET_KEY = "background-test-secret"
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{database_path}"
            SQLALCHEMY_TRACK_MODIFICATIONS = False
            DATABASE_AUTO_CREATE = False
            WTF_CSRF_ENABLED = False
            SECURITY_HEADERS_ENABLED = False
            BACKGROUND_ANALYSIS_ENABLED = True
            ANALYSIS_JOB_MAX_ATTEMPTS = 2

        self.app = create_app(TestConfig)
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()

        self.user = User(username="owner", email="owner@example.com")
        self.user.set_password("password")
        self.project = Project(
            project_id="project-1",
            project_name="Project",
            original_filename="project.zip",
            stored_filename="project.zip",
            file_type=".zip",
            file_size=100,
            project_path=self.temp_dir.name,
            user_id=1,
        )
        db.session.add(self.user)
        db.session.flush()
        self.project.user_id = self.user.id
        db.session.add(self.project)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()
        self.temp_dir.cleanup()

    def test_enqueue_and_claim_job(self):
        job = enqueue_analysis(self.project, self.user, max_attempts=2)
        self.assertEqual(job.status, "queued")
        self.assertEqual(job.progress, 0)

        claimed = claim_next_job()
        self.assertEqual(claimed.id, job.id)
        self.assertEqual(claimed.status, "running")
        self.assertEqual(claimed.attempts, 1)
        self.assertEqual(claimed.progress, 5)

    def test_failed_job_retries_then_stops(self):
        job = enqueue_analysis(self.project, self.user, max_attempts=2)
        claimed = claim_next_job()
        fail_job(claimed, RuntimeError("first failure"))

        retried = db.session.get(AnalysisJob, job.id)
        self.assertEqual(retried.status, "queued")
        self.assertIn("first failure", retried.error_message)

        claimed_again = claim_next_job()
        fail_job(claimed_again, RuntimeError("second failure"))
        failed = db.session.get(AnalysisJob, job.id)
        self.assertEqual(failed.status, "failed")
        self.assertEqual(failed.progress, 100)

    @patch("helpers.background_analysis.run_project_analysis")
    def test_completed_job_links_analysis(self, run_analysis):
        analysis = Analysis(
            project_id=self.project.id,
            user_id=self.user.id,
            filename="project.zip",
            status="Completed",
        )
        db.session.add(analysis)
        db.session.commit()
        run_analysis.return_value = {"analysis_id": analysis.id}

        job = enqueue_analysis(self.project, self.user)
        claimed = claim_next_job()
        process_job(claimed)

        completed = db.session.get(AnalysisJob, job.id)
        self.assertEqual(completed.status, "completed")
        self.assertEqual(completed.progress, 100)
        self.assertEqual(completed.analysis_id, analysis.id)


if __name__ == "__main__":
    unittest.main()
