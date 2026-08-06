"""Secure account-management routes for Sentrix."""

import hashlib
import shutil
from pathlib import Path

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, logout_user
from flask_mail import Message
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from database import db
from extensions import mail
from forms import ChangePasswordForm, ForgotPasswordForm, ResetPasswordForm
from models import Analysis, Project, Review, User
from settings_models import UserSettings


account_bp = Blueprint("account", __name__)
_TOKEN_SALT = "sentrix-password-reset-v2"


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def _password_fingerprint(user):
    return hashlib.sha256(user.password_hash.encode("utf-8")).hexdigest()[:24]


def _generate_token(user):
    return _serializer().dumps(
        {"user_id": user.id, "password": _password_fingerprint(user)},
        salt=_TOKEN_SALT,
    )


def _verify_token(token):
    try:
        payload = _serializer().loads(
            token,
            salt=_TOKEN_SALT,
            max_age=int(current_app.config.get("PASSWORD_RESET_MAX_AGE", 3600)),
        )
    except (BadSignature, SignatureExpired, TypeError, ValueError):
        return None

    user = db.session.get(User, payload.get("user_id"))
    if user is None or payload.get("password") != _password_fingerprint(user):
        return None
    return user


def _remove_path(path):
    if not path:
        return

    try:
        candidate = Path(path)
        if candidate.is_dir():
            shutil.rmtree(candidate, ignore_errors=True)
        elif candidate.is_file():
            candidate.unlink(missing_ok=True)
    except (OSError, TypeError, ValueError):
        current_app.logger.exception("Unable to remove account-owned path: %s", path)


@account_bp.route("/forgot-password", methods=["GET"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("main.profile"))
    return render_template("forgot_password.html", form=ForgotPasswordForm())


@account_bp.post("/password-reset/request")
def password_reset_request():
    form = ForgotPasswordForm()
    if not form.validate_on_submit():
        return render_template("forgot_password.html", form=form), 400

    normalized_email = form.email.data.strip().lower()
    user = User.query.filter(db.func.lower(User.email) == normalized_email).first()

    if user is not None:
        token = _generate_token(user)
        reset_url = url_for("account.reset_password", token=token, _external=True)
        expires_minutes = int(current_app.config.get("PASSWORD_RESET_MAX_AGE", 3600)) // 60
        sender = (
            current_app.config.get("MAIL_DEFAULT_SENDER")
            or current_app.config.get("MAIL_USERNAME")
            or current_app.config.get("SUPPORT_EMAIL")
        )
        message = Message(
            subject="Reset your Sentrix password",
            sender=sender,
            recipients=[user.email],
            body=(
                f"Hello {user.username},\n\n"
                "A password reset was requested for your Sentrix account.\n\n"
                f"Reset your password: {reset_url}\n\n"
                f"This link expires in {expires_minutes} minutes.\n\n"
                "If you did not request this, ignore this email."
            ),
        )
        try:
            mail.send(message)
        except Exception:
            current_app.logger.exception("Unable to send password-reset email")

    flash(
        "If an account exists with that email, password reset instructions have been sent.",
        "success",
    )
    return redirect(url_for("main.login"))


@account_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = _verify_token(token)
    if user is None:
        flash("That password reset link is invalid or has expired.", "danger")
        return redirect(url_for("account.forgot_password"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has been updated. You can now sign in.", "success")
        return redirect(url_for("main.login"))

    return render_template("reset_password.html", form=form, token=token)


@account_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            form.current_password.errors.append("Your current password is incorrect.")
        elif current_user.check_password(form.new_password.data):
            form.new_password.errors.append("Your new password must be different.")
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            logout_user()
            flash("Password changed successfully. Please sign in again.", "success")
            return redirect(url_for("main.login"))

    return render_template("change_password.html", form=form)


@account_bp.route("/account/delete", methods=["GET", "POST"])
@login_required
def delete_account():
    if request.method == "GET":
        return render_template("delete_account.html")

    password = request.form.get("password", "")
    confirmation = request.form.get("confirmation", "").strip()

    if not current_user.check_password(password):
        flash("Your password is incorrect.", "danger")
        return render_template("delete_account.html"), 400

    if confirmation != "DELETE":
        flash('Type "DELETE" exactly to confirm permanent account removal.', "danger")
        return render_template("delete_account.html"), 400

    user_id = current_user.id
    user = db.session.get(User, user_id)
    projects = Project.query.filter_by(user_id=user_id).all()
    analyses = Analysis.query.filter_by(user_id=user_id).all()

    for analysis in analyses:
        _remove_path(analysis.report_path)

    for project in projects:
        _remove_path(project.project_path)

    if user and user.profile_picture and user.profile_picture != "default.png":
        upload_root = Path(current_app.config["UPLOAD_FOLDER"])
        _remove_path(upload_root / "profile_pics" / user.profile_picture)

    try:
        UserSettings.query.filter_by(user_id=user_id).delete(synchronize_session=False)
        Review.query.filter_by(user_id=user_id).delete(synchronize_session=False)
        Analysis.query.filter_by(user_id=user_id).delete(synchronize_session=False)
        Project.query.filter_by(user_id=user_id).delete(synchronize_session=False)

        logout_user()
        if user is not None:
            db.session.delete(user)
        db.session.commit()

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to delete Sentrix account %s", user_id)
        flash("Your account could not be deleted. Please try again.", "danger")
        return redirect(url_for("account.delete_account"))

    flash("Your Sentrix account and associated data were permanently deleted.", "success")
    return redirect(url_for("main.home"))
