import json
import subprocess


def run_pylint(file_path):
    """
    Run pylint and return structured results.
    """

    try:

        result = subprocess.run(
            [
                "pylint",
                file_path,
                "--output-format=json"
            ],
            capture_output=True,
            text=True
        )

        issues = []

        score = 10.0

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
            data = []

        text_result = subprocess.run(
            [
                "pylint",
                file_path
            ],
            capture_output=True,
            text=True
        )

        for line in text_result.stdout.splitlines():

            if "rated at" in line:

                try:

                    score = float(
                        line.split("rated at")[1]
                        .split("/")[0]
                        .strip()
                    )

                except Exception:

                    pass

        return {

            "score": score,

            "issues": issues,

            "output": text_result.stdout

        }

    except Exception as error:

        return {

            "score": 0,

            "issues": [],

            "output": str(error)

        }
