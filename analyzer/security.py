import json
import subprocess


def run_bandit(path):
    """
    Run Bandit recursively and return structured security results.

    Returns:
        {
            "count": int,
            "issues": list,
            "output": str
        }
    """

    try:
        result = subprocess.run(
            [
                "bandit",
                "-r",
                path,
                "-f",
                "json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        raw_output = (
            result.stdout
            + "\n"
            + result.stderr
        ).strip()

        try:
            data = json.loads(result.stdout or "{}")
        except json.JSONDecodeError:
            return {
                "count": 0,
                "issues": [],
                "output": raw_output,
            }

        issues = []

        for item in data.get("results", []):
            issues.append(
                {
                    "file": item.get("filename"),
                    "line": item.get("line_number"),
                    "column": item.get("col_offset"),
                    "severity": item.get("issue_severity"),
                    "confidence": item.get("issue_confidence"),
                    "issue": item.get("issue_text"),
                    "test_id": item.get("test_id"),
                    "test_name": item.get("test_name"),
                    "code": item.get("code"),
                }
            )

        return {
            "count": len(issues),
            "issues": issues,
            "output": raw_output,
        }

    except Exception as error:
        return {
            "count": 0,
            "issues": [str(error)],
            "output": str(error),
        }
