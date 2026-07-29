import os
import shutil
import zipfile


IGNORED_DIRECTORIES = {
    "venv",
    ".venv",
    "__pycache__",
    ".git",
    ".idea",
    ".vscode",
    "node_modules"
}


def extract_project(upload_path, extract_folder):
    """
    Extract a Python project and return all Python source files.

    Supports:
    - ZIP archives
    - Single Python files
    """

    # --------------------------------------------------
    # Single Python file
    # --------------------------------------------------

    if upload_path.lower().endswith(".py"):
        return [upload_path]

    # --------------------------------------------------
    # Validate ZIP file
    # --------------------------------------------------

    if not zipfile.is_zipfile(upload_path):
        raise ValueError("Uploaded file is not a valid ZIP archive.")

    # --------------------------------------------------
    # Prepare extraction directory
    # --------------------------------------------------

    if os.path.exists(extract_folder):
        shutil.rmtree(extract_folder)

    os.makedirs(extract_folder, exist_ok=True)

    # --------------------------------------------------
    # Safe extraction
    # --------------------------------------------------

    with zipfile.ZipFile(upload_path, "r") as zip_ref:

        for member in zip_ref.infolist():

            destination = os.path.abspath(
                os.path.join(
                    extract_folder,
                    member.filename
                )
            )

            if not destination.startswith(
                os.path.abspath(extract_folder)
            ):
                raise ValueError(
                    "Unsafe ZIP archive detected."
                )

        zip_ref.extractall(extract_folder)

    # --------------------------------------------------
    # Collect Python files
    # --------------------------------------------------

    python_files = []

    for root, dirs, files in os.walk(extract_folder):

        dirs[:] = [
            directory
            for directory in dirs
            if directory not in IGNORED_DIRECTORIES
        ]

        for file in files:

            if file.lower().endswith(".py"):

                python_files.append(
                    os.path.join(root, file)
                )

    return python_files
