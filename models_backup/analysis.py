from datetime import datetime

from database import db


class Analysis(db.Model):
    __tablename__ = "analyses"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    overall_score = db.Column(
        db.Float,
        default=0
    )

    pylint_score = db.Column(
        db.Float,
        default=0
    )

    security_issues = db.Column(
        db.Integer,
        default=0
    )

    formatting_status = db.Column(
        db.String(50),
        default="Unknown"
    )

    ai_summary = db.Column(
        db.Text
    )

    ai_recommendations = db.Column(
        db.Text
    )

    pylint_report = db.Column(
        db.Text
    )

    bandit_report = db.Column(
        db.Text
    )

    radon_report = db.Column(
        db.Text
    )

    report_json = db.Column(
        db.String(500)
    )

    report_html = db.Column(
        db.String(500)
    )

    report_pdf = db.Column(
        db.String(500)
    )

    scan_duration = db.Column(
        db.Float,
        default=0
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    project_id = db.Column(
        db.Integer,
        db.ForeignKey("projects.id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    def __repr__(self):
        return f"<Analysis {self.id}>"
