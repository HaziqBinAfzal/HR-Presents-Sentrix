"""Compatibility loader for the legacy route module.

The legacy ``main.py`` still contains a small number of malformed duplicate
blocks. This loader removes only those known blocks before compiling the module,
allowing the production route overrides to be installed normally.
"""

from pathlib import Path


_SOURCE_PATH = Path(__file__).with_name("main.py")


def _remove_malformed_dashboard_block(source: str) -> str:
    lines = source.splitlines(keepends=True)
    cleaned = []
    index = 0
    removed = False

    while index < len(lines):
        line = lines[index]

        if not removed and line.startswith("        recent_activities.append({"):
            removed = True
            index += 1

            while index < len(lines):
                if lines[index].startswith("        })"):
                    index += 1
                    break
                index += 1

            continue

        cleaned.append(line)
        index += 1

    if not removed:
        raise RuntimeError(
            "The expected malformed dashboard block was not found in "
            "analyzer/routes/main.py. Refusing to modify unknown source."
        )

    return "".join(cleaned)


def _remove_malformed_duplicate_review_route(source: str) -> str:
    start_marker = (
        '@main.route("/reviews/delete/<int:review_id>", methods=["POST"])\n'
        "@login_required\n"
        "def remove_review(review_id):"
    )
    end_marker = "# REPORT DOWNLOAD #"

    start = source.find(start_marker)
    if start == -1:
        raise RuntimeError(
            "The expected malformed duplicate review route was not found in "
            "analyzer/routes/main.py. Refusing to modify unknown source."
        )

    end = source.find(end_marker, start)
    if end == -1:
        raise RuntimeError(
            "The report-download marker following the malformed review route "
            "was not found. Refusing to modify unknown source."
        )

    return source[:start] + source[end:]


def _remove_trailing_duplicate_review_handlers(source: str) -> str:
    marker = (
        '# ============================================================\n'
        '# EDIT REVIEW\n'
        '# ============================================================\n\n'
        '@main.route("/reviews/edit/<int:review_id>", methods=["GET", "POST"])'
    )

    first = source.find(marker)
    if first == -1:
        raise RuntimeError(
            "The primary edit-review route was not found in analyzer/routes/main.py."
        )

    second = source.find(marker, first + len(marker))
    if second == -1:
        raise RuntimeError(
            "The trailing duplicate edit-review route was not found in "
            "analyzer/routes/main.py. Refusing to modify unknown source."
        )

    # The duplicate edit/delete handlers are the final block in the legacy file.
    return source[:second].rstrip() + "\n"


_source = _SOURCE_PATH.read_text(encoding="utf-8")
_source = _remove_malformed_dashboard_block(_source)
_source = _remove_malformed_duplicate_review_route(_source)
_source = _remove_trailing_duplicate_review_handlers(_source)
_namespace = {
    "__name__": "analyzer.routes.main_runtime",
    "__file__": str(_SOURCE_PATH),
    "__package__": "analyzer.routes",
}
exec(compile(_source, str(_SOURCE_PATH), "exec"), _namespace)

main = _namespace["main"]
