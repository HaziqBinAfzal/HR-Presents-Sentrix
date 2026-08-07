from pathlib import Path

import black


def run_black(file_path):
    """Check Black formatting in-process so packaged builds need no external CLI."""
    try:
        source = Path(file_path).read_text(encoding="utf-8", errors="ignore")
        try:
            black.format_file_contents(
                source,
                fast=True,
                mode=black.FileMode(),
            )
        except black.NothingChanged:
            return {
                "passed": True,
                "status": "Passed",
                "output": "Already formatted with Black.",
            }

        return {
            "passed": False,
            "status": "Needs Formatting",
            "output": "Black would reformat this file.",
        }
    except Exception as error:
        return {
            "passed": False,
            "status": "Error",
            "output": f"Black analyzer error: {error}",
            "error": str(error),
        }
