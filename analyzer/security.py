import json
import subprocess


def run_bandit(path):
    """
    Run Bandit recursively and return structured results.
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
            text=True
        )

        data = json.loads(result.stdout)

        issues = []

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

        return {
            "count": len(issues),
            "issues": issues,
            "output": json.dumps(data, indent=4)
        }

    except Exception as error:

        return {
            "count": 0,
            "issues": [],
            "output": str(error)
        }
