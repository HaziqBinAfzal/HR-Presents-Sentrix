import json
import subprocess


def run_bandit(path):
    """
    Run Bandit recursively on a file or directory.

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
                "json"
            ],
            capture_output=True,
            text=True,
            check=False
        )

        output = (
            result.stdout +
            "\n" +
            result.stderr
        ).strip()

        issues = []

        try:
            data = json.loads(result.stdout)

            for item in data.get("results", []):
                issues.append(
                    {
                        "file": item.get("filename"),
                        "line": item.get("line_number"),
                        "severity": item.get("issue_severity"),
                        "confidence": item.get("issue_confidence"),
                        "issue": item.get("issue_text")
                    }
                )

        except Exception:
            pass

        return {
            "count": len(issues),
            "issues": issues,
            "output": output
        }

    except Exception as error:
        return {
            "count": 0,
            "issues": [str(error)],
            "output": str(error)
        }
