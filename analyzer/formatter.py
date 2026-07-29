import subprocess


def run_black(file_path):
    """
    Run Black in check mode on a Python file.

    Returns:
        {
            "passed": bool,
            "status": str,
            "output": str
        }
    """

    try:

        result = subprocess.run(
            [
                "black",
                "--check",
                file_path
            ],
            capture_output=True,
            text=True,
            check=False
        )

        passed = result.returncode == 0

        output = (
            result.stdout +
            "\n" +
            result.stderr
        ).strip()

        return {
            "passed": passed,
            "status": (
                "Passed"
                if passed
                else "Needs Formatting"
            ),
            "output": output
        }

    except Exception as error:

        return {
            "passed": False,
            "status": "Error",
            "output": str(error)
        }
