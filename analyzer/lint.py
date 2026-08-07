import io
import json

from pylint.lint import Run
from pylint.reporters.json_reporter import JSONReporter


def _score_from_stats(stats):
    """Return a stable 0-10 Pylint score across supported Pylint versions."""
    if stats is None:
        return None

    global_note = getattr(stats, "global_note", None)
    if global_note is not None:
        try:
            return max(0.0, min(10.0, float(global_note)))
        except (TypeError, ValueError):
            pass

    def _count(name):
        try:
            return float(getattr(stats, name, 0) or 0)
        except (TypeError, ValueError):
            return 0.0

    statements = _count("statement")
    fatal = _count("fatal")
    error = _count("error")
    warning = _count("warning")
    refactor = _count("refactor")
    convention = _count("convention")

    total_messages = fatal + error + warning + refactor + convention

    # Pylint's default evaluation is based on weighted message counts per
    # statement. Clamp to the 0-10 range used by the Sentrix UI.
    if statements > 0:
        penalty = ((5.0 * (fatal + error) + warning + refactor + convention) / statements) * 10.0
        return max(0.0, min(10.0, 10.0 - penalty))

    # A successfully linted file with no statements and no findings is clean.
    if total_messages == 0:
        return 10.0

    return 0.0


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
        score = _score_from_stats(stats)

        # If Pylint completed and produced no findings but its stats object did
        # not expose a score, do not misreport a clean file as 0/10.
        if score is None:
            score = 10.0 if not issues else 0.0

        return {
            "score": round(float(score), 2),
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
