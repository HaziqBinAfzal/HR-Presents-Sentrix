from datetime import datetime

from database import db


class UserSettings(db.Model):
    """Persistent per-user settings for Sentrix."""

    __tablename__ = "user_settings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    analysis_mode = db.Column(db.String(30), nullable=False, default="standard")
    report_format = db.Column(db.String(20), nullable=False, default="html")

    enable_black = db.Column(db.Boolean, nullable=False, default=True)
    enable_bandit = db.Column(db.Boolean, nullable=False, default=True)
    enable_radon = db.Column(db.Boolean, nullable=False, default=True)
    enable_pylint = db.Column(db.Boolean, nullable=False, default=True)
    enable_ai = db.Column(db.Boolean, nullable=False, default=True)

    auto_run_analysis = db.Column(db.Boolean, nullable=False, default=True)
    auto_generate_report = db.Column(db.Boolean, nullable=False, default=True)
    auto_delete_archive = db.Column(db.Boolean, nullable=False, default=False)
    save_analysis_history = db.Column(db.Boolean, nullable=False, default=True)

    notify_complete = db.Column(db.Boolean, nullable=False, default=True)
    notify_failed = db.Column(db.Boolean, nullable=False, default=True)
    notify_security = db.Column(db.Boolean, nullable=False, default=True)
    weekly_summary = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    user = db.relationship(
        "User",
        backref=db.backref("sentrix_settings", uselist=False, cascade="all, delete-orphan"),
    )

    @classmethod
    def for_user(cls, user_id):
        settings = cls.query.filter_by(user_id=user_id).first()
        if settings is None:
            settings = cls(user_id=user_id)
            db.session.add(settings)
            db.session.commit()
        return settings
