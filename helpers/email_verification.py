"""Signed email-verification tokens and authentication route integration."""

from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user
from flask_mail import Message
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from database import db
from extensions import mail
from forms import LoginForm, RegisterForm
from models import User

_TOKEN_SALT = "sentrix-email-verification-v1"


def _serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def generate_email_verification_token(user: User) -> str:
    """Create a token bound to both the user and their current email address."""
    return _serializer().dumps(
        {"user_id": user.id, "email": user.email.strip().lower()},
        salt=_TOKEN_SALT,
    )


def verify_email_verification_token(token: str) -> User | None:
    max_age = int(current_app.config.get("EMAIL_VERIFICATION_MAX_AGE", 86400))

    try:
        payload = _serializer().loads(token, salt=_TOKEN_SALT, max_age=max_age)
    except (BadSignature, SignatureExpired, TypeError, ValueError):
        return None

    user = db.session.get(User, payload.get("user_id"))
    if user is None:
        return None

    token_email = str(payload.get("email", "")).strip().lower()
    if token_email != user.email.strip().lower():
        return None

    return user


def send_email_verification(user: User) -> None:
    token = generate_email_verification_token(user)
    verification_url = url_for("main.verify_email", token=token, _external=True)
    expires_hours = max(
        1,
        int(current_app.config.get("EMAIL_VERIFICATION_MAX_AGE", 86400)) // 3600,
    )

    message = Message(
        subject="Verify your Sentrix email address",
        recipients=[user.email],
    )
    message.body = (
        f"Hello {user.username},\n\n"
        "Welcome to Sentrix. Verify your email address to activate your account:\n\n"
        f"{verification_url}\n\n"
        f"This link expires in {expires_hours} hours. If you did not create this "
        "account, you can ignore this message."
    )
    mail.send(message)


def _deliver_verification_email(user: User) -> bool:
    try:
        send_email_verification(user)
        return True
    except Exception:
        current_app.logger.exception(
            "Unable to send email-verification message for user %s", user.id
        )
        return False


def install_email_verification_routes(blueprint) -> None:
    """Replace legacy register/login handlers and install verification endpoints."""

    def verified_register():
        if current_user.is_authenticated:
            return redirect(url_for("main.dashboard"))

        form = RegisterForm()
        if form.validate_on_submit():
            normalized_email = form.email.data.strip().lower()
            normalized_username = form.username.data.strip()

            if User.query.filter(db.func.lower(User.email) == normalized_email).first():
                flash("Email already registered.", "danger")
                return redirect(url_for("main.register"))

            if User.query.filter(User.username == normalized_username).first():
                flash("Username already exists.", "danger")
                return redirect(url_for("main.register"))

            user = User(
                username=normalized_username,
                email=normalized_email,
                email_verified=False,
                email_verified_at=None,
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()

            delivered = _deliver_verification_email(user)
            if delivered:
                flash(
                    "Registration successful. Check your email to verify your account.",
                    "success",
                )
            else:
                flash(
                    "Your account was created, but the verification email could not "
                    "be sent. Use the resend form after SMTP is configured.",
                    "warning",
                )
            return redirect(
                url_for("main.verification_pending", email=user.email)
            )

        return render_template("register.html", form=form)

    def verified_login():
        if current_user.is_authenticated:
            return redirect(url_for("main.dashboard"))

        form = LoginForm()
        if form.validate_on_submit():
            normalized_email = form.email.data.strip().lower()
            user = User.query.filter(db.func.lower(User.email) == normalized_email).first()

            if user and user.check_password(form.password.data):
                if not user.email_verified:
                    flash(
                        "Verify your email address before signing in.",
                        "warning",
                    )
                    return redirect(
                        url_for("main.verification_pending", email=user.email)
                    )

                login_user(user, remember=bool(form.remember.data))
                flash("Login successful!", "success")
                next_url = request.args.get("next")
                if next_url and next_url.startswith("/") and not next_url.startswith("//"):
                    return redirect(next_url)
                return redirect(url_for("main.dashboard"))

            flash("Invalid email or password.", "danger")

        return render_template("login.html", form=form)

    blueprint.view_functions["register"] = verified_register
    blueprint.view_functions["login"] = verified_login

    @blueprint.get("/verify-email/<token>", endpoint="verify_email")
    def verify_email(token):
        user = verify_email_verification_token(token)
        if user is None:
            flash("That verification link is invalid or has expired.", "danger")
            return redirect(url_for("main.verification_pending"))

        if not user.email_verified:
            user.mark_email_verified()
            db.session.commit()

        flash("Your email has been verified. You can now sign in.", "success")
        return redirect(url_for("main.login"))

    @blueprint.get("/verification-pending", endpoint="verification_pending")
    def verification_pending():
        return render_template(
            "verification_pending.html",
            email=request.args.get("email", ""),
        )

    @blueprint.post("/verification/resend", endpoint="resend_verification")
    def resend_verification():
        normalized_email = request.form.get("email", "").strip().lower()
        user = None
        if normalized_email:
            user = User.query.filter(
                db.func.lower(User.email) == normalized_email
            ).first()

        if user is not None and not user.email_verified:
            _deliver_verification_email(user)

        flash(
            "If an unverified account exists with that email, a new verification "
            "message has been sent.",
            "success",
        )
        return redirect(
            url_for("main.verification_pending", email=normalized_email)
        )
