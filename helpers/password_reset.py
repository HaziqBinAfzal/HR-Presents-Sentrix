"""Password-reset token, email, and route helpers for Sentrix."""

import hashlib

from flask import current_app, flash, redirect, render_template, url_for
from flask_mail import Message
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from database import db
from extensions import mail
from forms import ForgotPasswordForm, ResetPasswordForm
from models import User

_TOKEN_SALT = "sentrix-password-reset-v1"


def _serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def _password_fingerprint(user: User) -> str:
    """Bind a token to the current password so successful use invalidates it."""
    return hashlib.sha256(user.password_hash.encode("utf-8")).hexdigest()[:24]


def generate_password_reset_token(user: User) -> str:
    return _serializer().dumps(
        {"user_id": user.id, "password": _password_fingerprint(user)},
        salt=_TOKEN_SALT,
    )


def verify_password_reset_token(token: str) -> User | None:
    max_age = int(current_app.config.get("PASSWORD_RESET_MAX_AGE", 3600))

    try:
        payload = _serializer().loads(token, salt=_TOKEN_SALT, max_age=max_age)
    except (BadSignature, SignatureExpired, TypeError, ValueError):
        return None

    user = db.session.get(User, payload.get("user_id"))
    if user is None:
        return None

    if payload.get("password") != _password_fingerprint(user):
        return None

    return user


def _send_password_reset_email(user: User) -> None:
    token = generate_password_reset_token(user)
    reset_url = url_for("main.reset_password_token", token=token, _external=True)
    expires_minutes = int(current_app.config.get("PASSWORD_RESET_MAX_AGE", 3600)) // 60

    message = Message(
        subject="Reset your Sentrix password",
        recipients=[user.email],
    )
    message.body = (
        f"Hello {user.username},\n\n"
        "A password reset was requested for your Sentrix account.\n\n"
        f"Reset your password: {reset_url}\n\n"
        f"This link expires in {expires_minutes} minutes and can be used only "
        "while your current password remains unchanged.\n\n"
        "If you did not request this, you can ignore this email."
    )
    mail.send(message)


def install_password_reset_routes(blueprint) -> None:
    """Install production password-reset endpoints on the main blueprint."""

    @blueprint.post("/password-reset/request", endpoint="password_reset_request")
    def password_reset_request():
        form = ForgotPasswordForm()

        if form.validate_on_submit():
            normalized_email = form.email.data.strip().lower()
            user = User.query.filter(db.func.lower(User.email) == normalized_email).first()

            if user is not None:
                try:
                    _send_password_reset_email(user)
                except Exception:
                    current_app.logger.exception(
                        "Unable to send password-reset email for user %s", user.id
                    )

            flash(
                "If an account exists with that email, password reset "
                "instructions have been sent.",
                "success",
            )
            return redirect(url_for("main.login"))

        return render_template("forgot_password.html", form=form), 400

    @blueprint.route(
        "/reset-password/<token>",
        methods=["GET", "POST"],
        endpoint="reset_password_token",
    )
    def reset_password_token(token):
        user = verify_password_reset_token(token)
        if user is None:
            flash("That password reset link is invalid or has expired.", "danger")
            return redirect(url_for("main.forgot_password"))

        form = ResetPasswordForm()
        if form.validate_on_submit():
            user.set_password(form.password.data)
            db.session.commit()
            flash("Your password has been updated. You can now sign in.", "success")
            return redirect(url_for("main.login"))

        return render_template("reset_password.html", form=form, token=token)
