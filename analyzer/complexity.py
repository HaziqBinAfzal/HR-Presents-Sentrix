from pathlib import Path

from radon.complexity import cc_rank, cc_visit


def run_radon(path):
    """Run Radon in-process so packaged Windows builds need no external CLI."""
    try:
        source = Path(path).read_text(encoding="utf-8", errors="ignore")
        blocks = cc_visit(source)
        rows = []

        for block in blocks:
            complexity = int(getattr(block, "complexity", 0) or 0)
            rows.append(
                {
                    "function": getattr(block, "fullname", None)
                    or getattr(block, "name", "Unknown"),
                    "grade": cc_rank(complexity),
                    "complexity": complexity,
                }
            )

        return rows
    except Exception:
        return []
