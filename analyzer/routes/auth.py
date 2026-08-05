from datetime import datetime

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user
from flask_mail import Message

from auth_models import UserAuthState
from database import db
from extensions import mail
from helpers.auth_tokens import create_token, read_token
from models import User


auth = Blueprint("auth", __name__)


def _send_message(subject, recipient, body):
    sender = current_app.config.get("MAIL_DEFAULT_SENDER") or current_app.config.get("MAIL_USERNAME")
    if not sender:
        current_app.logger.warning("Mail sender is not configured; skipped %s email", subject)
        return False
    try:
        mail.send(Message(subject=subject, recipients=[recipient], body=body, sender=sender))
        return True
    except Exception:
        current_app.logger.exception("Failed to send authentication email to %s", recipient)
        return False


def _send_verification(user):
    token = create_token(user.id, "verify-email")
    link = url_for("auth.verify_email", token=token, _external=True)
    return _send_message(
        "Verify your Sentrix email",
        user.email,
        f"Hello {user.username},\n\nVerify your Sentrix email address:\n{link}\n\n"
        "This link expires automatically. If you did not create this account, ignore this message.",
    )


@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", request.form.get("password2", password))
        if not username or not email or len(password) < 8:
            flash("Provide a username, email, and password of at least 8 characters.", "danger")
        elif password != confirm:
            flash("Passwords do not match.", "danger")
        elif User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
            flash("That username or email is already registered.", "danger")
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.flush()
            UserAuthState.for_user(user)
            db.session.commit()
            _send_verification(user)
            flash("Registration successful. Check your email for a verification link.", "success")
            return redirect(url_for("auth.login"))
    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            state = UserAuthState.for_user(user)
            db.session.commit()
            if current_app.config.get("REQUIRE_EMAIL_VERIFICATION", False) and not state.email_verified:
                flash("Verify your email before signing in.", "warning")
                return redirect(url_for("auth.resend_verification", email=user.email))
            login_user(user, remember=bool(request.form.get("remember")))
            flash("Login successful!", "success")
            return redirect(request.args.get("next") or url_for("main.dashboard"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")


@auth.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = User.query.filter_by(email=email).first()
        if user:
            token = create_token(user.id, "reset-password")
            link = url_for("auth.reset_password", token=token, _external=True)
            _send_message(
                "Reset your Sentrix password",
                user.email,
                f"Reset your Sentrix password using this link:\n{link}\n\n"
                "If you did not request this, ignore the message.",
            )
        flash("If that account exists, password reset instructions have been sent.", "success")
        return redirect(url_for("auth.login"))
    return render_template("forgot_password.html")


@auth.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    max_age = current_app.config.get("PASSWORD_RESET_MAX_AGE", 3600)
    user_id = read_token(token, "reset-password", max_age)
    user = db.session.get(User, user_id) if user_id else None
    if not user:
        flash("That password reset link is invalid or expired.", "danger")
        return redirect(url_for("auth.forgot_password"))
    if request.method == "POST":
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        if len(password) < 8:
            flash("Password must contain at least 8 characters.", "danger")
        elif password != confirm:
            flash("Passwords do not match.", "danger")
        else:
            user.set_password(password)
            state = UserAuthState.for_user(user)
            state.password_changed_at = datetime.utcnow()
            db.session.commit()
            flash("Your password has been reset. You can now sign in.", "success")
            return redirect(url_for("auth.login"))
    return render_template("reset_password.html", token=token)


@auth.route("/verify-email/<token>")
def verify_email(token):
    max_age = current_app.config.get("EMAIL_VERIFICATION_MAX_AGE", 86400)
    user_id = read_token(token, "verify-email", max_age)
    user = db.session.get(User, user_id) if user_id else None
    if not user:
        flash("That verification link is invalid or expired.", "danger")
        return redirect(url_for("auth.login"))
    state = UserAuthState.for_user(user)
    state.email_verified = True
    state.email_verified_at = datetime.utcnow()
    db.session.commit()
    flash("Your email has been verified.", "success")
    return redirect(url_for("auth.login"))


@auth.route("/resend-verification", methods=["GET", "POST"])
def resend_verification():
    email = (request.form.get("email") or request.args.get("email") or "").strip().lower()
    if request.method == "POST" or email:
        user = User.query.filter_by(email=email).first()
        if user:
            state = UserAuthState.for_user(user)
            db.session.commit()
            if not state.email_verified:
                _send_verification(user)
        flash("If verification is required, a new link has been sent.", "success")
        return redirect(url_for("auth.login"))
    return render_template("forgot_password.html")
