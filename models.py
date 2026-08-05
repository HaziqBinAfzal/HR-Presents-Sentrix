from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from database import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    full_name = db.Column(db.String(160), nullable=True)
    organization = db.Column(db.String(160), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    role = db.Column(db.String(80), nullable=False, default="Developer")
    workspace = db.Column(db.String(160), nullable=False, default="Personal Workspace")

    profile_picture = db.Column(
        db.String(255),
        nullable=True,
        default="default.png",
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    email_verified = db.Column(db.Boolean, nullable=False, default=False)
    email_verified_at = db.Column(db.DateTime, nullable=True)
    verification_sent_at = db.Column(db.DateTime, nullable=True)

    failed_login_attempts = db.Column(db.Integer, nullable=False, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    last_login_at = db.Column(db.DateTime, nullable=True)
    last_login_ip = db.Column(db.String(64), nullable=True)
    password_changed_at = db.Column(db.DateTime, nullable=True)

    two_factor_enabled = db.Column(db.Boolean, nullable=False, default=False)
    two_factor_secret = db.Column(db.String(255), nullable=True)
    backup_codes_hash = db.Column(db.Text, nullable=True)

    analyses = db.relationship(
        "Analysis",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan",
    )
    projects = db.relationship(
        "Project",
        backref="owner",
        lazy=True,
        cascade="all, delete-orphan",
    )
    reviews = db.relationship(
        "Review",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan",
    )
    auth_tokens = db.relationship(
        "AuthToken",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan",
    )
    sessions = db.relationship(
        "UserSession",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan",
    )
    audit_logs = db.relationship(
        "AuditLog",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        self.password_changed_at = datetime.utcnow()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_locked(self):
        return bool(self.locked_until and self.locked_until > datetime.utcnow())

    def __repr__(self):
        return f"<User {self.username}>"


class AuthToken(db.Model):
    __tablename__ = "auth_tokens"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    token_hash = db.Column(db.String(64), unique=True, nullable=False, index=True)
    token_type = db.Column(db.String(40), nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)
    revoked_at = db.Column(db.DateTime, nullable=True)

    @property
    def is_active(self):
        return (
            self.used_at is None
            and self.revoked_at is None
            and self.expires_at > datetime.utcnow()
        )


class UserSession(db.Model):
    __tablename__ = "user_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    session_hash = db.Column(db.String(64), unique=True, nullable=False, index=True)
    ip_address = db.Column(db.String(64), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_seen_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    revoked_at = db.Column(db.DateTime, nullable=True)

    @property
    def is_active(self):
        return self.revoked_at is None and self.expires_at > datetime.utcnow()


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    action = db.Column(db.String(120), nullable=False, index=True)
    outcome = db.Column(db.String(30), nullable=False, default="success")
    ip_address = db.Column(db.String(64), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    details = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    project_name = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    project_path = db.Column(db.String(500), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"<Project {self.project_id}: {self.project_name}>"


class Analysis(db.Model):
    __tablename__ = "analyses"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(
        db.Integer,
        db.ForeignKey("projects.id"),
        nullable=False,
        index=True,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    filename = db.Column(db.String(255), nullable=False)
    language = db.Column(db.String(50), nullable=False, default="Python")
    overall_score = db.Column(db.Float, nullable=False, default=0.0)
    pylint_score = db.Column(db.Float, nullable=False, default=0.0)
    security_count = db.Column(db.Integer, nullable=False, default=0)
    formatting_status = db.Column(db.String(30), nullable=False, default="Passed")
    complexity = db.Column(db.String(30), nullable=False, default="Low")
    analysis_duration = db.Column(db.Float, nullable=False, default=0.0)
    total_files = db.Column(db.Integer, nullable=False, default=0)
    total_lines = db.Column(db.Integer, nullable=False, default=0)
    ai_summary = db.Column(db.Text, nullable=True)
    recommendations = db.Column(db.Text, nullable=True)
    pylint_output = db.Column(db.Text, nullable=True)
    bandit_output = db.Column(db.Text, nullable=True)
    radon_output = db.Column(db.Text, nullable=True)
    issues_count = db.Column(db.Integer, nullable=False, default=0)
    functions_count = db.Column(db.Integer, nullable=False, default=0)
    classes_count = db.Column(db.Integer, nullable=False, default=0)
    comments_count = db.Column(db.Integer, nullable=False, default=0)
    blank_lines = db.Column(db.Integer, nullable=False, default=0)
    report_path = db.Column(db.String(255), nullable=True)
    syntax_output = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), nullable=False, default="Completed")
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )

    project = db.relationship(
        "Project",
        backref=db.backref(
            "analyses",
            lazy=True,
            cascade="all, delete-orphan",
        ),
    )

    def __repr__(self):
        return f"<Analysis {self.id}: {self.filename}>"


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"<Review {self.rating}★ {self.title}>"
