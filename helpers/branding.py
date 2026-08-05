"""Centralized Sentrix branding compatibility for legacy templates."""

from flask import url_for


BRAND_REPLACEMENTS = (
    ("CodeSentinel AI", "Sentrix"),
    ("CodeSentinelAI", "Sentrix"),
    ("Code Sentinel AI", "Sentrix"),
    ("CodeSentinel", "Sentrix"),
)


def register_branding(app):
    """Normalize legacy template copy and load the cleanup script on HTML pages."""

    @app.after_request
    def apply_sentrix_branding(response):
        if not response.is_json and response.mimetype == "text/html":
            html = response.get_data(as_text=True)

            for old_name, new_name in BRAND_REPLACEMENTS:
                html = html.replace(old_name, new_name)

            script_tag = (
                f'<script src="{url_for("static", filename="js/sentrix-branding.js")}" '
                'defer></script>'
            )

            if script_tag not in html and "</body>" in html:
                html = html.replace("</body>", f"{script_tag}\n</body>")

            response.set_data(html)
            response.headers["Content-Length"] = str(len(response.get_data()))

        return response
