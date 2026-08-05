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


def create_email_verification_token(user):
    active_tokens = AuthToken.query.filter_by(
        user_id=user.id,
        token_type="email_verification",
    ).all()
    now = datetime.utcnow()
    for token in active_tokens:
        if token.used_at is None and token.revoked_at is None:
            token.revoked_at = now

    raw_token = secrets.token_urlsafe(48)
    expires_at = now + timedelta(
        seconds=current_app.config["EMAIL_VERIFICATION_TOKEN_MAX_AGE"]
    )

    db.session.add(
        AuthToken(
            user_id=user.id,
            token_hash=_hash_token(raw_token),
            token_type="email_verification",
            expires_at=expires_at,
        )
    )
    user.verification_sent_at = now
    db.session.commit()
    return raw_token


def consume_email_verification_token(raw_token):
    token = AuthToken.query.filter_by(
        token_hash=_hash_token(raw_token),
        token_type="email_verification",
    ).first()

    if not token or not token.is_active:
        return None

    token.used_at = datetime.utcnow()
    db.session.commit()
    return token.user


def send_verification_email(user, raw_token):
    verification_url = url_for(
        "auth.verify_email",
        token=raw_token,
        _external=True,
    )

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
