import json
import re
import subprocess

SCORE_PATTERN = re.compile(r"rated at ([0-9]+\.[0-9]+)/10")


def run_pylint(file_path):
    """
    Run pylint on a Python file.

    Returns:
        {
            "score": float,
            "issues": list,
            "output": str
        }
    """

    try:
        result = subprocess.run(
            [
                "pylint",
                file_path,
                "--output-format=json"
            ],
            capture_output=True,
            text=True,
            check=False
        )

        issues = []

        try:
            data = json.loads(result.stdout)

            for item in data:
                issues.append(
                    {
                        "file": item.get("path"),
                        "line": item.get("line"),
                        "column": item.get("column"),
                        "type": item.get("type"),
                        "symbol": item.get("symbol"),
                        "message": item.get("message"),
                        "message_id": item.get("message-id")
                    }
                )

        except Exception:
            pass

        text_result = subprocess.run(
            [
                "pylint",
                file_path
            ],
            capture_output=True,
            text=True,
            check=False
        )

        score = 0.0

        match = SCORE_PATTERN.search(text_result.stdout)

        if match:
            score = float(match.group(1))

        return {
            "score": score,
            "issues": issues,
            "output": text_result.stdout
        }

    except Exception as error:
        return {
            "score": 0.0,
            "issues": [str(error)],
            "output": str(error)
        }
