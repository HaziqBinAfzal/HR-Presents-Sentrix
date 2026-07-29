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
        "codesentinel-secret-key"
    )

    # --------------------------------------------------
    # Database
    # --------------------------------------------------

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(INSTANCE_DIR, "database.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

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

    # Maximum upload size: 16 MB
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
