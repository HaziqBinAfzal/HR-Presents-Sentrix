import json
import subprocess
from pathlib import Path


def run_bandit(path):
    """Run Bandit recursively and return structured findings."""
    target = str(Path(path))

    try:
        result = subprocess.run(
            ["bandit", "-r", target, "-f", "json"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return {
            "count": 0,
            "issues": [],
            "output": "Bandit is not installed or is not available on PATH.",
        }
    except OSError as error:
        return {
            "count": 0,
            "issues": [],
            "output": str(error),
        }

    raw_output = (result.stdout or "").strip()
    error_output = (result.stderr or "").strip()

    try:
        data = json.loads(raw_output) if raw_output else {}
    except json.JSONDecodeError:
        return {
            "count": 0,
            "issues": [],
            "output": "\n".join(part for part in (raw_output, error_output) if part),
        }

    issues = []
    for item in data.get("results", []):
        issues.append(
            {
                "file": item.get("filename"),
                "line": item.get("line_number"),
                "severity": item.get("issue_severity"),
                "confidence": item.get("issue_confidence"),
                "issue": item.get("issue_text"),
                "test_id": item.get("test_id"),
                "test_name": item.get("test_name"),
            }
        )

    output = json.dumps(data, indent=2)
    if error_output:
        output = f"{output}\n{error_output}".strip()

    return {
        "count": len(issues),
        "issues": issues,
        "output": output,
    }
