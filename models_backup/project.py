from datetime import datetime

from database import db


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    project_uuid = db.Column(
        db.String(64),
        unique=True,
        nullable=False
    )

    project_name = db.Column(
        db.String(255),
        nullable=False
    )

    original_filename = db.Column(
        db.String(255),
        nullable=False
    )

    stored_filename = db.Column(
        db.String(255),
        nullable=False
    )

    extension = db.Column(
        db.String(20),
        nullable=False
    )

    project_path = db.Column(
        db.String(500),
        nullable=False
    )

    report_path = db.Column(
        db.String(500)
    )

    total_files = db.Column(
        db.Integer,
        default=0
    )

    python_files = db.Column(
        db.Integer,
        default=0
    )

    project_size = db.Column(
        db.BigInteger,
        default=0
    )

    upload_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    last_scan = db.Column(
        db.DateTime
    )

    status = db.Column(
        db.String(30),
        default="Uploaded"
    )

    language = db.Column(
        db.String(50),
        default="Python"
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    analyses = db.relationship(
        "Analysis",
        backref="project",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Project {self.project_name}>"
