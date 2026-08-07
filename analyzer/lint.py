import io
import json

from pylint.lint import Run
from pylint.reporters.json_reporter import JSONReporter


def run_pylint(file_path):
    """Run Pylint in-process so packaged Windows builds need no external CLI."""
    output = io.StringIO()
    reporter = JSONReporter(output=output)

    try:
        run = Run(
            [file_path, "--score=y"],
            reporter=reporter,
            exit=False,
        )

        try:
            data = json.loads(output.getvalue() or "[]")
        except json.JSONDecodeError:
            data = []

        issues = []
        for item in data:
            issues.append(
                {
                    "file": item.get("path"),
                    "line": item.get("line"),
                    "column": item.get("column"),
                    "type": item.get("type"),
                    "symbol": item.get("symbol"),
                    "message": item.get("message"),
                    "message_id": item.get("message-id"),
                }
            )

        stats = getattr(run.linter, "stats", None)
        score = float(getattr(stats, "global_note", 0.0) or 0.0)

        return {
            "score": score,
            "issues": issues,
            "output": output.getvalue().strip(),
        }
    except Exception as error:
        return {
            "score": 0.0,
            "issues": [],
            "output": f"Pylint analyzer error: {error}",
            "error": str(error),
        }
