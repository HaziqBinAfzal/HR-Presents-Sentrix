import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")

# Make sure instance directory exists
os.makedirs(INSTANCE_DIR, exist_ok=True)


class Config:

    # --------------------------------------------------
    # Flask
    # --------------------------------------------------

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        os.urandom(32).hex()
    )

    # --------------------------------------------------
    # Database
    # --------------------------------------------------

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(INSTANCE_DIR, "database.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True
    }

    # --------------------------------------------------
    # Upload Configuration
    # --------------------------------------------------

    UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        "uploads"
    )

    TEMP_FOLDER = os.path.join(
        UPLOAD_FOLDER,
        "temp"
    )

    PROJECT_FOLDER = os.path.join(
        UPLOAD_FOLDER,
        "projects"
    )

    REPORT_FOLDER = os.path.join(
        UPLOAD_FOLDER,
        "reports"
    )

    CORRECTED_FOLDER = os.path.join(
        UPLOAD_FOLDER,
        "corrected"
    )

    DIFF_FOLDER = os.path.join(
        UPLOAD_FOLDER,
        "diff"
    )

<<<<<<< HEAD
    # --------------------------------------------------
# Create Required Directories
# --------------------------------------------------

    for folder in (
      UPLOAD_FOLDER,
      TEMP_FOLDER,
      PROJECT_FOLDER,
      REPORT_FOLDER,
      CORRECTED_FOLDER,
      DIFF_FOLDER
    ):
      os.makedirs(folder, exist_ok=True)

    # Maximum upload size: 100 MB
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024
=======
    # Maximum upload size: 100 MB
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024

    # --------------------------------------------------
    # Mail Configuration
    # --------------------------------------------------

    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_USERNAME")
>>>>>>> origin/backend
