from pylint.lint import Run
from pylint.reporters import BaseReporter


class CollectingReporter(BaseReporter):
    """Collect Pylint messages directly instead of parsing reporter text output."""

    def __init__(self):
        super().__init__()
        self.issues = []

    def handle_message(self, msg):
        self.issues.append(
            {
                "file": getattr(msg, "path", None),
                "line": getattr(msg, "line", None),
                "column": getattr(msg, "column", None),
                "type": getattr(msg, "category", None),
                "symbol": getattr(msg, "symbol", None),
                "message": getattr(msg, "msg", ""),
                "message_id": getattr(msg, "msg_id", None),
            }
        )

    def _display(self, layout):
        # Reports are disabled for Sentrix; this satisfies BaseReporter.
        return None


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

    if statements > 0:
        penalty = (
            (5.0 * (fatal + error) + warning + refactor + convention)
            / statements
        ) * 10.0
        return max(0.0, min(10.0, 10.0 - penalty))

    if total_messages == 0:
        return 10.0

    return 0.0


def _format_output(issues):
    if not issues:
        return "No Pylint findings."

    return "\n\n".join(
        (
            f"{item.get('file') or 'Unknown file'}\n"
            f"Line {item.get('line') or 'Unknown'}\n"
            f"{item.get('type') or 'Unknown'}\n"
            f"{item.get('symbol') or item.get('message_id') or 'Unknown'}\n"
            f"{item.get('message') or ''}"
        )
        for item in issues
    )


def run_pylint(file_path):
    """Run Pylint in-process so packaged Windows builds need no external CLI."""
    reporter = CollectingReporter()

    try:
        run = Run(
            [file_path, "--score=y", "--reports=n"],
            reporter=reporter,
            exit=False,
        )

        issues = reporter.issues
        stats = getattr(run.linter, "stats", None)
        score = _score_from_stats(stats)

        if score is None:
            score = 10.0 if not issues else 0.0

        return {
            "score": round(float(score), 2),
            "issues": issues,
            "output": _format_output(issues),
        }
    except Exception as error:
        return {
            "score": 0.0,
            "issues": [],
            "output": f"Pylint analyzer error: {error}",
            "error": str(error),
        }
