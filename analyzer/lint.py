import re
import subprocess


def run_pylint(file_path):
    """
    Run Pylint and return the score plus all reported issues.
    """

    try:
        result = subprocess.run(
            ["pylint", file_path],
            capture_output=True,
            text=True,
        )

        output = result.stdout

        score = 0.0

        match = re.search(
            r"rated at ([0-9]+\.[0-9]+)/10",
            output,
        )

        if match:
            score = float(match.group(1))

        issues = []

        for line in output.splitlines():

            if ":" in line and (
                "C" in line
                or "W" in line
                or "E" in line
                or "R" in line
            ):
                issues.append(line)

        return {
            "score": score,
            "issues": issues,
            "output": output,
        }

    except Exception as e:

        return {
            "score": 0,
            "issues": [str(e)],
            "output": "",
        }
