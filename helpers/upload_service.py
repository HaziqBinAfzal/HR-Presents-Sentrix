import os
import uuid

from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {"py", "zip"}

MAX_FILE_SIZE = 16 * 1024 * 1024  # 16 MB


def allowed_file(filename):
    """
    Check whether the uploaded file has an allowed extension.
    """
    return (
        bool(filename)
        and "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def get_extension(filename):
    """
    Return the file extension without the dot.
    """
    if not filename or "." not in filename:
        return ""

    return filename.rsplit(".", 1)[1].lower()


def get_project_name(filename):
    """
    Return the filename without its extension.
    """
    if not filename:
        return ""

    return os.path.splitext(filename)[0]


def get_file_size(file):
    """
    Return uploaded file size in bytes.
    """
    current_position = file.tell()

    file.seek(0, os.SEEK_END)
    size = file.tell()

    file.seek(current_position)

    return size


def secure_upload_name(filename):
    """
    Make the uploaded filename safe for filesystem storage.
    """
    return secure_filename(filename)


def generate_unique_filename(filename):
    """
    Generate a unique safe filename.

    Example:
        project.zip

    becomes:
        project_8f4a21c9.zip
    """

    safe_filename = secure_upload_name(filename)

    name, extension = os.path.splitext(safe_filename)

    unique_id = uuid.uuid4().hex[:8]

    return f"{name}_{unique_id}{extension}"


def validate_upload(file):
    """
    Validate uploaded file.

    Returns:
        (True, "Valid") on success
        (False, "Error message") on failure
    """

    if file is None:
        return False, "No file was uploaded."

    if not file.filename:
        return False, "No file selected."

    if not allowed_file(file.filename):
        return (
            False,
            "Unsupported file type. Only .py and .zip files are allowed."
        )

    try:
        size = get_file_size(file)
    except Exception:
        return False, "Unable to determine file size."

    if size > MAX_FILE_SIZE:
        return False, "File exceeds the maximum allowed size of 16 MB."

    return True, "Valid"


def build_metadata(file, stored_filename=None):
    """
    Build metadata for an uploaded file.
    """

    original_filename = file.filename

    safe_original_filename = secure_upload_name(
        original_filename
    )

    return {
        "filename": safe_original_filename,
        "original_filename": original_filename,
        "stored_filename": stored_filename or safe_original_filename,
        "project_name": get_project_name(
            safe_original_filename
        ),
        "extension": get_extension(
            safe_original_filename
        ),
        "size": get_file_size(file),
    }


def generate_project_id():
    """
    Generate a unique project ID.
    """
    return uuid.uuid4().hex


def create_project_workspace(base_folder, project_id):
    """
    Create the directory structure for a project.
    """

    project_folder = os.path.join(
        base_folder,
        project_id
    )

    folders = {
        "root": project_folder,

        "source": os.path.join(
            project_folder,
            "source"
        ),

        "reports": os.path.join(
            project_folder,
            "reports"
        ),

        "corrected": os.path.join(
            project_folder,
            "corrected"
        ),

        "diff": os.path.join(
            project_folder,
            "diff"
        )
    }

    for folder in folders.values():
        os.makedirs(
            folder,
            exist_ok=True
        )

    return folders
