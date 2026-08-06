"""Load the legacy route module with narrowly scoped compatibility cleanup."""

from pathlib import Path

from helpers.community_routes import install_community_routes
from helpers.email_verification import install_email_verification_routes
from helpers.password_reset import install_password_reset_routes


_SOURCE_PATH = Path(__file__).with_name("main.py")


def _remove_duplicate_remove_review(source: str) -> str:
    """Remove only the stale second remove-review handler when it is present."""
    marker = (
        '@main.route("/reviews/delete/<int:review_id>", methods=["POST"])\n'
        "@login_required\n"
        "def remove_review(review_id):"
    )

    first = source.find(marker)
    if first == -1:
        return source

    second = source.find(marker, first + len(marker))
    if second == -1:
        return source

    end_marker = "# REPORT DOWNLOAD #"
    end = source.find(end_marker, second)
    if end == -1:
        raise RuntimeError(
            "Duplicate remove-review route was found, but its expected report "
            "section boundary is missing; refusing to alter unknown source."
        )

    return source[:second] + source[end:]


_source = _SOURCE_PATH.read_text(encoding="utf-8")
_source = _remove_duplicate_remove_review(_source)
_namespace = {
    "__name__": "analyzer.routes.main_runtime",
    "__file__": str(_SOURCE_PATH),
    "__package__": "analyzer.routes",
}
exec(compile(_source, str(_SOURCE_PATH), "exec"), _namespace)

main = _namespace["main"]
install_email_verification_routes(main)
install_password_reset_routes(main)
install_community_routes(main)
