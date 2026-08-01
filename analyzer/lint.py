import re
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
    """

    try:

        result = subprocess.run(
            ["pylint", file_path],
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

        issues = []

        for line in output.splitlines():

            line = line.strip()

            if ISSUE_PATTERN.match(line):

                issues.append(line)

        return {
            "score": score,
            "issues": issues,
            "output": output
        }

    except Exception as error:

        return {
            "score": 0.0,
            "issues": [str(error)],
            "output": ""
        }
