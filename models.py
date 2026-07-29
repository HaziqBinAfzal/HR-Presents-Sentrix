from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from database import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    profile_picture = db.Column(
        db.String(255),
        nullable=True,
        default="default.png"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    analyses = db.relationship(
        "Analysis",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )
    
    reviews = db.relationship(
    "Review",
    backref="user",
    lazy=True,
    cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(
            self.password_hash,
            password
        )

    def __repr__(self):
        return f"<User {self.username}>"

class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    project_id = db.Column(
        db.String(64),
        unique=True,
        nullable=False,
        index=True
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

    file_type = db.Column(
        db.String(20),
        nullable=False
    )

    file_size = db.Column(
        db.Integer,
        nullable=False
    )

    project_path = db.Column(
        db.String(500),
        nullable=False
    )

    upload_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    def __repr__(self):
        return f"<Project {self.project_name}>"

class Analysis(db.Model):
    __tablename__ = "analyses"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    filename = db.Column(
        db.String(255),
        nullable=False
    )

    upload_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    overall_score = db.Column(
        db.Float
    )

    ai_summary = db.Column(
        db.Text
    )

    report_path = db.Column(
        db.String(255)
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    def __repr__(self):
        return f"<Analysis {self.filename}>"

class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    rating = db.Column(
        db.Integer,
        nullable=False
    )

    title = db.Column(
        db.String(150),
        nullable=False
    )

    comment = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    def __repr__(self):
        return f"<Review {self.title}>"
