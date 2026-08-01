import re
import subprocess


COMPLEXITY_PATTERN = re.compile(
    r"^\s*[FM]\s+\d+:\d+\s+([A-Za-z_][A-Za-z0-9_]*)\s+-\s+([A-F])\s+\((\d+)\)"
)


def run_radon(path):
    """
    Run Radon cyclomatic complexity analysis.

    Returns:
        [
            {
                "function": str,
                "grade": str,
                "complexity": int
            }
        ]
    """

    try:

        result = subprocess.run(
            [
                "radon",
                "cc",
                path,
                "-s"
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

        rows = []

        for line in output.splitlines():

            match = COMPLEXITY_PATTERN.search(
                line
            )

            if match:

                rows.append(
                    {
                        "function": match.group(1),
                        "grade": match.group(2),
                        "complexity": int(
                            match.group(3)
                        )
                    }
                )

        return rows

    except Exception:

        return []
