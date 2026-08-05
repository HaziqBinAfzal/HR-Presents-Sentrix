import hashlib
import secrets
from datetime import datetime, timedelta

from flask import current_app, url_for
from flask_mail import Message

from database import db
from extensions import mail
from models import AuthToken


def _hash_token(raw_token):
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def _revoke_active_tokens(user_id, token_type):
    now = datetime.utcnow()
    tokens = AuthToken.query.filter_by(
        user_id=user_id,
        token_type=token_type,
    ).all()
    for token in tokens:
        if token.used_at is None and token.revoked_at is None:
            token.revoked_at = now
    return now


def _create_token(user, token_type, max_age_seconds):
    now = _revoke_active_tokens(user.id, token_type)
    raw_token = secrets.token_urlsafe(48)
    db.session.add(
        AuthToken(
            user_id=user.id,
            token_hash=_hash_token(raw_token),
            token_type=token_type,
            expires_at=now + timedelta(seconds=max_age_seconds),
        )
    )
    db.session.commit()
    return raw_token


def _consume_token(raw_token, token_type):
    token = AuthToken.query.filter_by(
        token_hash=_hash_token(raw_token),
        token_type=token_type,
    ).first()
    if not token or not token.is_active:
        return None
    token.used_at = datetime.utcnow()
    db.session.commit()
    return token.user


def create_email_verification_token(user):
    raw_token = _create_token(
        user,
        "email_verification",
        current_app.config["EMAIL_VERIFICATION_TOKEN_MAX_AGE"],
    )
    user.verification_sent_at = datetime.utcnow()
    db.session.commit()
    return raw_token


def consume_email_verification_token(raw_token):
    return _consume_token(raw_token, "email_verification")


def create_password_reset_token(user):
    return _create_token(
        user,
        "password_reset",
        current_app.config["PASSWORD_RESET_TOKEN_MAX_AGE"],
    )


def consume_password_reset_token(raw_token):
    return _consume_token(raw_token, "password_reset")


def send_verification_email(user, raw_token):
    verification_url = url_for("auth.verify_email", token=raw_token, _external=True)
    message = Message(
        subject="Verify your Sentrix email address",
        recipients=[user.email],
    )
    message.body = (
        f"Hello {user.username},\n\n"
        "Welcome to Sentrix. Verify your email address using the link below:\n\n"
        f"{verification_url}\n\n"
        "This link expires in 24 hours. If you did not create this account, "
        "you can ignore this email."
    )
    mail.send(message)


def send_password_reset_email(user, raw_token):
    reset_url = url_for("auth.reset_password", token=raw_token, _external=True)
    message = Message(
        subject="Reset your Sentrix password",
        recipients=[user.email],
    )
    message.body = (
        f"Hello {user.username},\n\n"
        "A password reset was requested for your Sentrix account. Use the "
        "single-use link below:\n\n"
        f"{reset_url}\n\n"
        "This link expires in one hour. If you did not request this reset, "
        "you can safely ignore this email."
    )
    mail.send(message)
