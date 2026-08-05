"""Compatibility loader for the legacy route module.

The current legacy ``main.py`` contains one malformed, duplicate dashboard
activity block. This loader removes only that known block before compiling the
module, allowing the production route overrides to be installed normally.
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


_source = _SOURCE_PATH.read_text(encoding="utf-8")
_source = _remove_malformed_dashboard_block(_source)
_namespace = {
    "__name__": "analyzer.routes.main_runtime",
    "__file__": str(_SOURCE_PATH),
    "__package__": "analyzer.routes",
}
exec(compile(_source, str(_SOURCE_PATH), "exec"), _namespace)

main = _namespace["main"]
