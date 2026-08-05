from datetime import datetime

from database import db


class UserAuthState(db.Model):
    __tablename__ = "user_auth_states"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    email_verified = db.Column(db.Boolean, nullable=False, default=False)
    email_verified_at = db.Column(db.DateTime, nullable=True)
    password_changed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    user = db.relationship("User", backref=db.backref("auth_state", uselist=False))

    @classmethod
    def for_user(cls, user):
        state = cls.query.filter_by(user_id=user.id).first()
        if state is None:
            state = cls(user_id=user.id)
            db.session.add(state)
            db.session.flush()
        return state
