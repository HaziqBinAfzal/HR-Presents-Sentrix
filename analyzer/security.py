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
                "txt"
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

        for line in output.splitlines():

            line = line.strip()

            if line.startswith(">> Issue:"):

                issues.append(
                    line.replace(
                        ">> Issue:",
                        ""
                    ).strip()
                )

        return {
            "count": len(issues),
            "issues": issues,
            "output": output
        }

    except Exception as error:

        return {
            "count": 0,
            "issues": [str(error)],
            "output": ""
        }
