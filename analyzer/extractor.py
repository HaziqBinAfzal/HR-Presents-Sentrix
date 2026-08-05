import os
import shutil
import stat
import zipfile
from pathlib import Path, PurePosixPath


IGNORED_DIRECTORIES = {
    "venv",
    ".venv",
    "__pycache__",
    ".git",
    ".idea",
    ".vscode",
    "node_modules",
}

MAX_ARCHIVE_MEMBERS = 5000
MAX_ARCHIVE_UNCOMPRESSED_SIZE = 500 * 1024 * 1024
MAX_SINGLE_MEMBER_SIZE = 100 * 1024 * 1024
MAX_COMPRESSION_RATIO = 200
COPY_CHUNK_SIZE = 1024 * 1024


def _normalized_member_path(name):
    """Return a safe relative POSIX path or reject an unsafe archive member."""
    normalized_name = name.replace("\\", "/")
    member_path = PurePosixPath(normalized_name)

    if (
        not normalized_name
        or normalized_name.startswith("/")
        or member_path.is_absolute()
        or any(part in {"", ".", ".."} for part in member_path.parts)
        or (member_path.parts and ":" in member_path.parts[0])
    ):
        raise ValueError("Unsafe ZIP archive path detected.")

    return member_path


def _is_symlink(member):
    mode = (member.external_attr >> 16) & 0xFFFF
    return stat.S_ISLNK(mode)


def _validate_archive(zip_ref):
    members = zip_ref.infolist()
    if len(members) > MAX_ARCHIVE_MEMBERS:
        raise ValueError(
            f"ZIP archive contains too many entries; maximum is {MAX_ARCHIVE_MEMBERS}."
        )

    seen_paths = set()
    total_uncompressed = 0
    validated = []

    for member in members:
        member_path = _normalized_member_path(member.filename)
        canonical = member_path.as_posix().casefold()

        if canonical in seen_paths:
            raise ValueError("ZIP archive contains duplicate file paths.")
        seen_paths.add(canonical)

        if member.flag_bits & 0x1:
            raise ValueError("Encrypted ZIP archives are not supported.")

        if _is_symlink(member):
            raise ValueError("ZIP archives containing symbolic links are not supported.")

        if not member.is_dir():
            if member.file_size > MAX_SINGLE_MEMBER_SIZE:
                raise ValueError("ZIP archive contains a file larger than 100 MB.")

            total_uncompressed += member.file_size
            if total_uncompressed > MAX_ARCHIVE_UNCOMPRESSED_SIZE:
                raise ValueError("ZIP archive expands beyond the 500 MB safety limit.")

            if member.compress_size == 0:
                if member.file_size > 0:
                    raise ValueError("ZIP archive contains a suspicious compressed entry.")
            else:
                ratio = member.file_size / member.compress_size
                if ratio > MAX_COMPRESSION_RATIO:
                    raise ValueError("ZIP archive contains a suspicious compression ratio.")

            if member_path.suffix.lower() == ".zip":
                raise ValueError("Nested ZIP archives are not supported.")

        validated.append((member, member_path))

    return validated


def _extract_member(zip_ref, member, member_path, extract_root):
    destination = extract_root.joinpath(*member_path.parts)
    resolved_destination = destination.resolve()

    try:
        resolved_destination.relative_to(extract_root)
    except ValueError as exc:
        raise ValueError("Unsafe ZIP archive path detected.") from exc

    if member.is_dir():
        resolved_destination.mkdir(parents=True, exist_ok=True)
        return

    resolved_destination.parent.mkdir(parents=True, exist_ok=True)
    bytes_written = 0

    with zip_ref.open(member, "r") as source, resolved_destination.open("xb") as target:
        while True:
            chunk = source.read(COPY_CHUNK_SIZE)
            if not chunk:
                break
            bytes_written += len(chunk)
            if bytes_written > member.file_size or bytes_written > MAX_SINGLE_MEMBER_SIZE:
                raise ValueError("ZIP member exceeded its declared safe size.")
            target.write(chunk)

    if bytes_written != member.file_size:
        raise ValueError("ZIP member size did not match its archive metadata.")


def extract_project(upload_path, extract_folder):
    """Extract a Python upload safely and return discovered Python files."""
    if upload_path.lower().endswith(".py"):
        return [upload_path]

    if not zipfile.is_zipfile(upload_path):
        raise ValueError("Uploaded file is not a valid ZIP archive.")

    extract_root = Path(extract_folder).resolve()
    if extract_root.exists():
        shutil.rmtree(extract_root)
    extract_root.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(upload_path, "r") as zip_ref:
            validated_members = _validate_archive(zip_ref)
            for member, member_path in validated_members:
                _extract_member(zip_ref, member, member_path, extract_root)
    except Exception:
        shutil.rmtree(extract_root, ignore_errors=True)
        raise

    python_files = []
    for root, dirs, files in os.walk(extract_root):
        dirs[:] = [
            directory
            for directory in dirs
            if directory not in IGNORED_DIRECTORIES
        ]

        for filename in files:
            if filename.lower().endswith(".py"):
                python_files.append(os.path.join(root, filename))

    if not python_files:
        raise ValueError("No Python files were found in the uploaded project.")

    return sorted(python_files)
