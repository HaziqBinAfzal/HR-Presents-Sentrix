from datetime import datetime, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_wtf import FlaskForm

from auth.services import (
    consume_email_verification_token,
    consume_password_reset_token,
    create_email_verification_token,
    create_password_reset_token,
    send_password_reset_email,
    send_verification_email,
)
from database import db
from forms import ForgotPasswordForm, LoginForm, RegisterForm, ResetPasswordForm
from models import AuditLog, AuthToken, User, UserSession
from security.sessions import (
    create_tracked_session,
    get_current_tracked_session,
    revoke_current_session,
    revoke_session_for_user,
)


auth = Blueprint("auth", __name__)


class RevokeSessionForm(FlaskForm):
    pass


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
        send_verification_email(user, create_email_verification_token(user))
        flash("Account created. Check your email to verify your account.", "success")
    except Exception:
        flash("Account created, but the verification email could not be sent.", "warning")
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
    remember = bool(form.remember.data)
    login_user(user, remember=remember)
    create_tracked_session(user, remember=remember)
    return redirect(request.args.get("next") or url_for("main.dashboard"))


@auth.route("/logout")
@login_required
def logout():
    revoke_current_session()
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth.route("/sessions")
@login_required
def sessions():
    active_sessions = (
        UserSession.query
        .filter_by(user_id=current_user.id, revoked_at=None)
        .order_by(UserSession.last_seen_at.desc())
        .all()
    )
    current_session = get_current_tracked_session()
    return render_template(
        "auth/sessions.html",
        sessions=active_sessions,
        current_session_id=current_session.id if current_session else None,
        revoke_form=RevokeSessionForm(),
    )


@auth.route("/sessions/<int:session_id>/revoke", methods=["POST"])
@login_required
def revoke_session(session_id):
    form = RevokeSessionForm()
    if not form.validate_on_submit():
        flash("Invalid or expired security request.", "danger")
        return redirect(url_for("auth.sessions"))
    current_session = get_current_tracked_session()
    if not revoke_session_for_user(current_user.id, session_id):
        flash("Session not found or already revoked.", "warning")
        return redirect(url_for("auth.sessions"))
    _record_event("auth.session_revoked", user=current_user, details=f"session_id={session_id}")
    db.session.commit()
    if current_session and current_session.id == session_id:
        logout_user()
        flash("This device was signed out.", "info")
        return redirect(url_for("auth.login"))
    flash("Device session revoked successfully.", "success")
    return redirect(url_for("auth.sessions"))


@auth.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and user.email_verified:
            try:
                send_password_reset_email(user, create_password_reset_token(user))
                _record_event("auth.password_reset_requested", user=user)
                db.session.commit()
            except Exception:
                _record_event("auth.password_reset_email_failed", user=user, outcome="failure")
                db.session.commit()
        flash("If a verified account exists, a reset link has been sent.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/forgot_password.html", form=form)


@auth.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = consume_password_reset_token(token)
        if not user:
            flash("This password reset link is invalid or has expired.", "danger")
            return redirect(url_for("auth.forgot_password"))
        user.set_password(form.password.data)
        user.failed_login_attempts = 0
        user.locked_until = None
        now = datetime.utcnow()
        for tracked_session in UserSession.query.filter_by(user_id=user.id).all():
            if tracked_session.revoked_at is None:
                tracked_session.revoked_at = now
        for auth_token in AuthToken.query.filter_by(user_id=user.id).all():
            if auth_token.used_at is None and auth_token.revoked_at is None:
                auth_token.revoked_at = now
        _record_event("auth.password_reset_completed", user=user)
        db.session.commit()
        flash("Your password has been reset. You can now sign in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", form=form)


@auth.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ResetPasswordForm()
    if request.method == "POST":
        current_password = request.form.get("current_password", "")
        if not current_user.check_password(current_password):
            flash("Current password is incorrect.", "danger")
            return render_template("auth/change_password.html", form=form)
        if not form.validate_on_submit():
            return render_template("auth/change_password.html", form=form)
        current_user.set_password(form.password.data)
        now = datetime.utcnow()
        for tracked_session in UserSession.query.filter_by(user_id=current_user.id).all():
            if tracked_session.revoked_at is None:
                tracked_session.revoked_at = now
        _record_event("auth.password_changed", user=current_user)
        db.session.commit()
        logout_user()
        flash("Password changed. Sign in again with your new password.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/change_password.html", form=form)


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
    return render_template("auth/verification_pending.html", email=request.args.get("email", ""))


@auth.route("/resend-verification", methods=["POST"])
def resend_verification():
    email = request.form.get("email", "").strip().lower()
    user = User.query.filter_by(email=email).first()
    if user and not user.email_verified:
        try:
            send_verification_email(user, create_email_verification_token(user))
        except Exception:
            flash("Verification email could not be sent. Check mail configuration.", "danger")
            return redirect(url_for("auth.verification_pending", email=email))
    flash("If the account exists and is unverified, a new link has been sent.", "success")
    return redirect(url_for("auth.verification_pending", email=email))
