from datetime import UTC, datetime

from database import db


def utcnow():
    return datetime.now(UTC).replace(tzinfo=None)


class AnalysisJob(db.Model):
    __tablename__ = "analysis_jobs"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(
        db.Integer, db.ForeignKey("projects.id"), nullable=False, index=True
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    analysis_id = db.Column(
        db.Integer, db.ForeignKey("analyses.id"), nullable=True, index=True
    )
    status = db.Column(
        db.String(30), nullable=False, default="queued", server_default="queued", index=True
    )
    progress = db.Column(db.Integer, nullable=False, default=0, server_default="0")
    attempts = db.Column(db.Integer, nullable=False, default=0, server_default="0")
    max_attempts = db.Column(db.Integer, nullable=False, default=3, server_default="3")
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False, index=True)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(
        db.DateTime, default=utcnow, onupdate=utcnow, nullable=False
    )

    project = db.relationship("Project")
    user = db.relationship("User")
    analysis = db.relationship("Analysis")

    def as_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "analysis_id": self.analysis_id,
            "status": self.status,
            "progress": self.progress,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "error": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
