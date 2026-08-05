from flask_login import login_required

from analyzer.routes.production_routes import (
    dashboard,
    download_report,
    export_history_csv,
    profile,
    reports,
)


def install_production_routes(app):
    """Replace broken legacy handlers and add production-only routes."""
    app.view_functions["main.dashboard"] = login_required(dashboard)
    app.view_functions["main.profile"] = login_required(profile)

    if "main.reports" not in app.view_functions:
        app.add_url_rule(
            "/reports",
            endpoint="main.reports",
            view_func=login_required(reports),
            methods=["GET"],
        )
    if "main.download_report" not in app.view_functions:
        app.add_url_rule(
            "/reports/<int:analysis_id>/download",
            endpoint="main.download_report",
            view_func=login_required(download_report),
            methods=["GET"],
        )
    if "main.export_history_csv" not in app.view_functions:
        app.add_url_rule(
            "/history/export.csv",
            endpoint="main.export_history_csv",
            view_func=login_required(export_history_csv),
            methods=["GET"],
        )
