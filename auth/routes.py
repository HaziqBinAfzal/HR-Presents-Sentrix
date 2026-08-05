from datetime import datetime, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user

from auth.services import (
    consume_email_verification_token,
    create_email_verification_token,
    send_verification_email,
)
from database import db
from forms import LoginForm, RegisterForm
from models import AuditLog, User


auth = Blueprint("auth", __name__)


def _record_event(action, user=None, outcome="success", details=None):
    db.session.add(
        AuditLog(
            user_id=user.id if user else None,
            action=action,
            outcome=outcome,
            ip_address=request.headers.get("X-Forwarded-For", request.remote_addr),
            user_agent=request.user_agent.string[:1000],
            details=details,
        )
    )


@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegisterForm()
    if not form.validate_on_submit():
        return render_template("register.html", form=form)

    email = form.email.data.strip().lower()
    username = form.username.data.strip()

    if User.query.filter_by(email=email).first():
        flash("Email already registered.", "danger")
        return render_template("register.html", form=form)

    if User.query.filter_by(username=username).first():
        flash("Username already exists.", "danger")
        return render_template("register.html", form=form)

    user = User(username=username, email=email, email_verified=False)
    user.set_password(form.password.data)
    db.session.add(user)
    db.session.flush()
    _record_event("account.registered", user=user)
    db.session.commit()

    try:
        raw_token = create_email_verification_token(user)
        send_verification_email(user, raw_token)
        flash("Account created. Check your email to verify your account.", "success")
    except Exception:
        flash(
            "Account created, but the verification email could not be sent. "
            "Use the resend option after configuring email settings.",
            "warning",
        )

    return redirect(url_for("auth.verification_pending", email=user.email))


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if not form.validate_on_submit():
        return render_template("login.html", form=form)

    email = form.email.data.strip().lower()
    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(form.password.data):
        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=15)
            _record_event("auth.login", user=user, outcome="failure")
            db.session.commit()
        flash("Invalid email or password.", "danger")
        return render_template("login.html", form=form)

    if user.is_locked():
        flash("Account temporarily locked. Try again later.", "danger")
        return render_template("login.html", form=form)

    if not user.email_verified:
        flash("Verify your email address before signing in.", "warning")
        return redirect(url_for("auth.verification_pending", email=user.email))

    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = datetime.utcnow()
    user.last_login_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    _record_event("auth.login", user=user)
    db.session.commit()
    login_user(user, remember=form.remember.data)
    return redirect(request.args.get("next") or url_for("main.dashboard"))


@auth.route("/verify-email/<token>")
def verify_email(token):
    user = consume_email_verification_token(token)
    if not user:
        flash("This verification link is invalid or has expired.", "danger")
        return redirect(url_for("auth.login"))

    if not user.email_verified:
        user.email_verified = True
        user.email_verified_at = datetime.utcnow()
        _record_event("account.email_verified", user=user)
        db.session.commit()

    flash("Email verified successfully. You can now sign in.", "success")
    return redirect(url_for("auth.login"))


@auth.route("/verification-pending")
def verification_pending():
    return render_template(
        "auth/verification_pending.html",
        email=request.args.get("email", ""),
    )


@auth.route("/resend-verification", methods=["POST"])
def resend_verification():
    email = request.form.get("email", "").strip().lower()
    user = User.query.filter_by(email=email).first()

    if user and not user.email_verified:
        try:
            raw_token = create_email_verification_token(user)
            send_verification_email(user, raw_token)
        except Exception:
            flash("Verification email could not be sent. Check mail configuration.", "danger")
            return redirect(url_for("auth.verification_pending", email=email))

    flash("If the account exists and is unverified, a new link has been sent.", "success")
    return redirect(url_for("auth.verification_pending", email=email))
