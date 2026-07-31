import json
import subprocess


ISSUE_PATTERN = re.compile(
    r"^[CRWEFI]:\s*\d+,\d+:"
)

SCORE_PATTERN = re.compile(
    r"rated at ([0-9]+\.[0-9]+)/10"
)


def run_pylint(file_path):
    """

    Run Pylint on a Python file.

    Returns:
        {
            "score": float,
            "issues": list,
            "output": str
        }

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

            text=True,
            check=False
        )

        output = (
            result.stdout +
            "\n" +
            result.stderr
        ).strip()

        score = 0.0

        match = SCORE_PATTERN.search(
            output
        )

        if match:

            score = float(
                match.group(1)
            )


            text=True
        )


        issues = []

        score = 10.0


            line = line.strip()

            if ISSUE_PATTERN.match(line):

                issues.append(line)

        try:
            data = json.loads(result.stdout)

            for item in data:

                issues.append(
                    {
                        "file": item.get("path"),
                        "line": item.get("line"),
                        "type": item.get("type"),
                        "symbol": item.get("symbol"),
                        "message": item.get("message")
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

            "output": output


            "output": text_result.stdout


        }

    except Exception as error:

        return {

            "score": 0.0,
            "issues": [str(error)],
            "output": ""


            "score": 0,

            "issues": [],

            "output": str(error)


        }
