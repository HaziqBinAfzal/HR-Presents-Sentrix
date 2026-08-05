import json
import re
import subprocess


SCORE_PATTERN = re.compile(r"rated at\s+(-?\d+(?:\.\d+)?)/10")


def _run_pylint_command(file_path, output_format=None):
    command = ["pylint", file_path]
    if output_format:
        command.append(f"--output-format={output_format}")

    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )


def run_pylint(file_path):
    """Run Pylint and return a stable structured result."""
    try:
        json_result = _run_pylint_command(file_path, "json")
        text_result = _run_pylint_command(file_path)

        issues = []
        try:
            payload = json.loads(json_result.stdout or "[]")
        except json.JSONDecodeError:
            payload = []

        for item in payload:
            issues.append(
                {
                    "file": item.get("path") or file_path,
                    "line": item.get("line") or 0,
                    "column": item.get("column") or 0,
                    "type": item.get("type") or "unknown",
                    "symbol": item.get("symbol") or "unknown",
                    "message": item.get("message") or "",
                    "message_id": item.get("message-id") or "",
                }
            )

        combined_output = "\n".join(
            part.strip()
            for part in (text_result.stdout, text_result.stderr)
            if part and part.strip()
        )

        score = 0.0
        match = SCORE_PATTERN.search(combined_output)
        if match:
            score = float(match.group(1))

        return {
            "score": score,
            "issues": issues,
            "output": combined_output,
        }

    except FileNotFoundError:
        return {
            "score": 0.0,
            "issues": [],
            "output": "Pylint is not installed or is not available on PATH.",
        }
    except Exception as error:
        return {
            "score": 0.0,
            "issues": [],
            "output": str(error),
        }
