"""Benchmark Sentrix ZIP extraction with generated Python projects.

This script creates temporary ZIP archives containing a configurable number of
small Python files, extracts them through the production extractor, and reports
archive size, expanded size, creation time, extraction time, and peak traced
Python memory. It does not access the application database or persistent upload
folders.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
import tracemalloc
import zipfile
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from analyzer.extractor import MAX_ARCHIVE_MEMBERS, extract_project


DEFAULT_COUNTS = (100, 1000, 5000)
DEFAULT_LINES_PER_FILE = 25


def _python_source(index: int, lines_per_file: int) -> str:
    lines = [
        f'"""Generated benchmark module {index}."""',
        "",
        f"MODULE_INDEX = {index}",
        "",
        "def calculate(value):",
        "    total = value + MODULE_INDEX",
    ]
    while len(lines) < max(lines_per_file - 2, 6):
        lines.append(f"    total += {len(lines)}")
    lines.extend(["    return total", ""])
    return "\n".join(lines)


def _build_archive(path: Path, file_count: int, lines_per_file: int) -> tuple[float, int]:
    started = time.perf_counter()
    expanded_size = 0
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for index in range(file_count):
            content = _python_source(index, lines_per_file).encode("utf-8")
            expanded_size += len(content)
            archive.writestr(f"project/package_{index // 100:04d}/module_{index:05d}.py", content)
    return time.perf_counter() - started, expanded_size


def run_case(file_count: int, lines_per_file: int) -> dict[str, int | float]:
    if file_count < 1:
        raise ValueError("File count must be at least 1.")
    if file_count > MAX_ARCHIVE_MEMBERS:
        raise ValueError(
            f"File count {file_count} exceeds extractor member limit {MAX_ARCHIVE_MEMBERS}."
        )

    with tempfile.TemporaryDirectory(prefix="sentrix-benchmark-") as root:
        root_path = Path(root)
        archive_path = root_path / f"project-{file_count}.zip"
        extract_path = root_path / "extracted"

        create_seconds, expanded_size = _build_archive(
            archive_path,
            file_count,
            lines_per_file,
        )

        tracemalloc.start()
        extract_started = time.perf_counter()
        extracted_files = extract_project(str(archive_path), str(extract_path))
        extract_seconds = time.perf_counter() - extract_started
        _, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        if len(extracted_files) != file_count:
            raise RuntimeError(
                f"Expected {file_count} extracted Python files, got {len(extracted_files)}."
            )

        return {
            "files": file_count,
            "lines_per_file": lines_per_file,
            "archive_bytes": archive_path.stat().st_size,
            "expanded_bytes": expanded_size,
            "create_seconds": round(create_seconds, 4),
            "extract_seconds": round(extract_seconds, 4),
            "files_per_second": round(file_count / extract_seconds, 2),
            "peak_traced_memory_bytes": peak_bytes,
        }


def _human_bytes(value: int) -> str:
    units = ("B", "KiB", "MiB", "GiB")
    amount = float(value)
    for unit in units:
        if amount < 1024 or unit == units[-1]:
            return f"{amount:.2f} {unit}"
        amount /= 1024
    return f"{value} B"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--counts",
        nargs="+",
        type=int,
        default=list(DEFAULT_COUNTS),
        help="File counts to benchmark (default: 100 1000 5000).",
    )
    parser.add_argument(
        "--lines-per-file",
        type=int,
        default=DEFAULT_LINES_PER_FILE,
        help=f"Generated lines per Python file (default: {DEFAULT_LINES_PER_FILE}).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON instead of a formatted table.",
    )
    args = parser.parse_args()

    results = [run_case(count, args.lines_per_file) for count in args.counts]

    if args.json:
        print(json.dumps(results, indent=2))
        return 0

    print("Sentrix extractor benchmark")
    print(f"Member safety limit: {MAX_ARCHIVE_MEMBERS}")
    print()
    header = (
        f"{'Files':>7}  {'Archive':>11}  {'Expanded':>11}  "
        f"{'Create(s)':>10}  {'Extract(s)':>11}  {'Files/s':>10}  {'Peak memory':>12}"
    )
    print(header)
    print("-" * len(header))
    for result in results:
        print(
            f"{result['files']:>7}  "
            f"{_human_bytes(int(result['archive_bytes'])):>11}  "
            f"{_human_bytes(int(result['expanded_bytes'])):>11}  "
            f"{result['create_seconds']:>10.4f}  "
            f"{result['extract_seconds']:>11.4f}  "
            f"{result['files_per_second']:>10.2f}  "
            f"{_human_bytes(int(result['peak_traced_memory_bytes'])):>12}"
        )

    print()
    print("Temporary archives and extracted files were deleted automatically.")
    print("Peak memory is Python allocation memory measured by tracemalloc, not total process RSS.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
