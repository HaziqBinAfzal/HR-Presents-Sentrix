import re
import subprocess


def run_radon(path):
    """
    Run Radon complexity analysis.
    """

    try:

        result = subprocess.run(
            [
                "radon",
                "cc",
                path,
                "-s",
            ],
            capture_output=True,
            text=True,
        )

        rows = []

        pattern = re.compile(
            r"^\s*[FM]\s+\d+:\d+\s+([A-Za-z_][A-Za-z0-9_]*)\s+-\s+([A-F])\s+\((\d+)\)"
        )

        for line in result.stdout.splitlines():

            match = pattern.search(line)

            if match:

                rows.append(
                    {
                        "function": match.group(1),
                        "grade": match.group(2),
                        "complexity": int(match.group(3)),
                    }
                )

        return rows

    except Exception:

        return []
