import subprocess


def run_black(file_path):
    """
    Run Black in check mode against a Python file.
    """

    try:
        result = subprocess.run(
            ["black", "--check", file_path],
            capture_output=True,
            text=True,
        )

        return {
            "passed": result.returncode == 0,
            "status": "Passed" if result.returncode == 0 else "Needs Formatting",
            "output": result.stdout + result.stderr,
        }

    except Exception as e:
        return {
            "passed": False,
            "status": "Error",
            "output": str(e),
        }
