from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

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

    projects = db.relationship(
        "Project",
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

    notifications = db.relationship(
        "Notification",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    usage = db.relationship(
        "UserUsage",
        backref="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    ai_settings = db.relationship(
        "UserAISettings",
        backref="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(
            password
        )

    def check_password(self, password):
        return check_password_hash(
            self.password_hash,
            password
        )

    def __repr__(self):
        return f"<User {self.username}>"
