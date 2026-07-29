import subprocess


def run_bandit(path):
    """
    Run Bandit recursively on a file or directory.
    """

    try:
        result = subprocess.run(
            [
                "bandit",
                "-r",
                path,
                "-f",
                "txt",
            ],
            capture_output=True,
            text=True,
        )

        output = result.stdout

        issues = []

        for line in output.splitlines():

            line = line.strip()

            if line.startswith(">> Issue:"):
                issues.append(line.replace(">> Issue:", "").strip())

        return {
            "count": len(issues),
            "issues": issues,
            "output": output,
        }

    except Exception as e:

        return {
            "count": 0,
            "issues": [str(e)],
            "output": "",
        }
