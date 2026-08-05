import os
from datetime import timedelta

from dotenv import load_dotenv


load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)


def _env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


class Config:
    """Base configuration shared by local and production deployments."""

    ENVIRONMENT = os.getenv("APP_ENV", "development").lower()
    SECRET_KEY = os.getenv("SECRET_KEY")

    if not SECRET_KEY:
        if ENVIRONMENT == "production":
            raise RuntimeError("SECRET_KEY must be set when APP_ENV=production")
        SECRET_KEY = "development-only-change-me"

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(INSTANCE_DIR, "database.db"),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    TEMP_FOLDER = os.path.join(UPLOAD_FOLDER, "temp")
    PROJECT_FOLDER = os.path.join(UPLOAD_FOLDER, "projects")
    REPORT_FOLDER = os.path.join(UPLOAD_FOLDER, "reports")
    CORRECTED_FOLDER = os.path.join(UPLOAD_FOLDER, "corrected")
    DIFF_FOLDER = os.path.join(UPLOAD_FOLDER, "diff")

    for folder in (
        UPLOAD_FOLDER,
        TEMP_FOLDER,
        PROJECT_FOLDER,
        REPORT_FOLDER,
        CORRECTED_FOLDER,
        DIFF_FOLDER,
    ):
        os.makedirs(folder, exist_ok=True)

    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 100 * 1024 * 1024))

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_COOKIE_SECURE = _env_bool("SESSION_COOKIE_SECURE", ENVIRONMENT == "production")
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = _env_bool("REMEMBER_COOKIE_SECURE", ENVIRONMENT == "production")
    PERMANENT_SESSION_LIFETIME = timedelta(
        minutes=int(os.getenv("SESSION_LIFETIME_MINUTES", "120"))
    )

    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = _env_bool("MAIL_USE_TLS", True)
    MAIL_USE_SSL = _env_bool("MAIL_USE_SSL", False)
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", MAIL_USERNAME)
    SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "supportsentrix@gmail.com")
    PASSWORD_RESET_MAX_AGE = int(os.getenv("PASSWORD_RESET_MAX_AGE", "3600"))
    EMAIL_VERIFICATION_MAX_AGE = int(
        os.getenv("EMAIL_VERIFICATION_MAX_AGE", "86400")
    )

    SECURITY_HEADERS_ENABLED = _env_bool("SECURITY_HEADERS_ENABLED", True)
    HSTS_ENABLED = _env_bool("HSTS_ENABLED", ENVIRONMENT == "production")
    HSTS_MAX_AGE = int(os.getenv("HSTS_MAX_AGE", "31536000"))
    CONTENT_SECURITY_POLICY = os.getenv(
        "CONTENT_SECURITY_POLICY",
        "default-src 'self'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'none'; "
        "object-src 'none'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data: https:; "
        "style-src 'self' 'unsafe-inline' https:; "
        "script-src 'self' 'unsafe-inline' https:; "
        "connect-src 'self' https:; "
        "upgrade-insecure-requests",
    )
    PERMISSIONS_POLICY = os.getenv(
        "PERMISSIONS_POLICY",
        "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
    )
    REFERRER_POLICY = os.getenv(
        "REFERRER_POLICY",
        "strict-origin-when-cross-origin",
    )

    PREFERRED_URL_SCHEME = os.getenv(
        "PREFERRED_URL_SCHEME", "https" if ENVIRONMENT == "production" else "http"
    )
