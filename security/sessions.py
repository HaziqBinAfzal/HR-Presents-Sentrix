import hashlib
import secrets
from datetime import datetime, timedelta

from flask import current_app, request, session
from flask_login import current_user, logout_user

from database import db
from models import AuditLog, UserSession


def _hash_session_token(raw_token):
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def _client_ip():
    forwarded = request.headers.get("X-Forwarded-For", "")
    return (forwarded.split(",", 1)[0].strip() or request.remote_addr or "")[:64]


def create_tracked_session(user, remember=False):
    raw_token = secrets.token_urlsafe(48)
    now = datetime.utcnow()
    lifetime = (
        current_app.config["REMEMBER_SESSION_LIFETIME_SECONDS"]
        if remember
        else current_app.config["SESSION_LIFETIME_SECONDS"]
    )
    tracked = UserSession(
        user_id=user.id,
        session_hash=_hash_session_token(raw_token),
        ip_address=_client_ip(),
        user_agent=request.user_agent.string[:1000],
        created_at=now,
        last_seen_at=now,
        expires_at=now + timedelta(seconds=lifetime),
    )
    db.session.add(tracked)
    db.session.commit()
    session["sentrix_session_token"] = raw_token
    session.permanent = bool(remember)
    return tracked


def get_current_tracked_session():
    raw_token = session.get("sentrix_session_token")
    if not raw_token or not current_user.is_authenticated:
        return None
    return UserSession.query.filter_by(
        user_id=current_user.id,
        session_hash=_hash_session_token(raw_token),
    ).first()


def validate_current_session():
    if not current_user.is_authenticated:
        return True
    tracked = get_current_tracked_session()
    now = datetime.utcnow()
    if not tracked or not tracked.is_active:
        logout_user()
        session.pop("sentrix_session_token", None)
        return False
    idle_timeout = timedelta(seconds=current_app.config["SESSION_IDLE_TIMEOUT_SECONDS"])
    if tracked.last_seen_at and now - tracked.last_seen_at > idle_timeout:
        tracked.revoked_at = now
        db.session.add(
            AuditLog(
                user_id=current_user.id,
                action="auth.session_expired",
                outcome="success",
                ip_address=_client_ip(),
                user_agent=request.user_agent.string[:1000],
            )
        )
        db.session.commit()
        logout_user()
        session.pop("sentrix_session_token", None)
        return False
    tracked.last_seen_at = now
    db.session.commit()
    return True


def revoke_current_session(action="auth.logout"):
    tracked = get_current_tracked_session()
    if tracked and tracked.revoked_at is None:
        tracked.revoked_at = datetime.utcnow()
    if current_user.is_authenticated:
        db.session.add(
            AuditLog(
                user_id=current_user.id,
                action=action,
                outcome="success",
                ip_address=_client_ip(),
                user_agent=request.user_agent.string[:1000],
            )
        )
    db.session.commit()
    session.pop("sentrix_session_token", None)


def revoke_session_for_user(user_id, session_id):
    tracked = UserSession.query.filter_by(id=session_id, user_id=user_id).first()
    if not tracked or tracked.revoked_at is not None:
        return False
    tracked.revoked_at = datetime.utcnow()
    db.session.commit()
    return True
