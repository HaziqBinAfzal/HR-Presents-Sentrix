import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(32).hex())

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

    MAX_CONTENT_LENGTH = 100 * 1024 * 1024

    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "false").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", MAIL_USERNAME)
    SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", MAIL_USERNAME)
