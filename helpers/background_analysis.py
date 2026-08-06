from datetime import UTC, datetime

from background_models import AnalysisJob
from database import db
from helpers.analysis_service import run_project_analysis
from models import Project, User


def utcnow():
    return datetime.now(UTC).replace(tzinfo=None)


def enqueue_analysis(project, user, *, max_attempts=3):
    job = AnalysisJob(
        project_id=project.id,
        user_id=user.id,
        status="queued",
        progress=0,
        max_attempts=max_attempts,
    )
    db.session.add(job)
    db.session.commit()
    return job


def claim_next_job():
    job = (
        AnalysisJob.query.filter_by(status="queued")
        .order_by(AnalysisJob.created_at.asc(), AnalysisJob.id.asc())
        .first()
    )
    if job is None:
        return None

    job.status = "running"
    job.progress = 5
    job.attempts += 1
    job.started_at = utcnow()
    job.error_message = None
    db.session.commit()
    return job


def process_job(job):
    project = db.session.get(Project, job.project_id)
    user = db.session.get(User, job.user_id)
    if project is None or user is None:
        raise RuntimeError("Analysis job references a missing project or user.")

    job.progress = 15
    db.session.commit()

    result = run_project_analysis(project, user)

    job.analysis_id = result["analysis_id"]
    job.status = "completed"
    job.progress = 100
    job.completed_at = utcnow()
    job.error_message = None
    db.session.commit()
    return result


def fail_job(job, error):
    db.session.rollback()
    job = db.session.get(AnalysisJob, job.id)
    if job is None:
        return

    job.error_message = str(error)[:4000]
    if job.attempts < job.max_attempts:
        job.status = "queued"
        job.progress = 0
        job.started_at = None
    else:
        job.status = "failed"
        job.progress = 100
        job.completed_at = utcnow()
    db.session.commit()
