import os
import shutil
import zipfile


def extract_project(upload_path, extract_folder):
    """
    Extract a ZIP project and return all Python files.
    If the uploaded file is already a .py file,
    simply return that file.
    """

    if upload_path.endswith(".py"):
        return [upload_path]

    if os.path.exists(extract_folder):
        shutil.rmtree(extract_folder)

    os.makedirs(extract_folder, exist_ok=True)

    with zipfile.ZipFile(upload_path, "r") as zip_ref:
        zip_ref.extractall(extract_folder)

    python_files = []

    for root, dirs, files in os.walk(extract_folder):

        for file in files:

            if file.endswith(".py"):

                python_files.append(
                    os.path.join(root, file)
                )

    return python_files
