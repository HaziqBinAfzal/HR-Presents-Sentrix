import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"


class Config:
    """Sentrix application configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        raise RuntimeError(
            "SECRET_KEY is required. Copy .env.example to .env and set a stable secret."
        )

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{INSTANCE_DIR / 'database.db'}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    UPLOAD_FOLDER = Path(os.getenv("UPLOAD_FOLDER", BASE_DIR / "uploads"))
    TEMP_FOLDER = UPLOAD_FOLDER / "temp"
    PROJECT_FOLDER = UPLOAD_FOLDER / "projects"
    REPORT_FOLDER = UPLOAD_FOLDER / "reports"
    CORRECTED_FOLDER = UPLOAD_FOLDER / "corrected"
    DIFF_FOLDER = UPLOAD_FOLDER / "diff"

    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 100 * 1024 * 1024))

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "0") == "1"

    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "1") == "1"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "0") == "1"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv(
        "MAIL_DEFAULT_SENDER",
        MAIL_USERNAME or "supportsentrix@gmail.com",
    )

    @classmethod
    def ensure_directories(cls):
        """Create application-owned directories during app initialization."""
        for folder in (
            INSTANCE_DIR,
            cls.UPLOAD_FOLDER,
            cls.TEMP_FOLDER,
            cls.PROJECT_FOLDER,
            cls.REPORT_FOLDER,
            cls.CORRECTED_FOLDER,
            cls.DIFF_FOLDER,
        ):
            Path(folder).mkdir(parents=True, exist_ok=True)
