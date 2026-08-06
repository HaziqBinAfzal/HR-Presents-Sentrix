import os

from flask import Flask, render_template
from flask_login import LoginManager, current_user

from analyzer.routes.account import account_bp
from analyzer.routes.main_loader import main
from analyzer.routes.settings import settings_bp
from analyzer.routes.settings_alias import settings_page
from analyzer.routes.upload import upload_bp
from config import Config
from database import db
from extensions import csrf, mail, migrate
from models import Analysis, Project, User
from settings_models import UserSettings  # noqa: F401 - registers the model before schema checks


login_manager = LoginManager()
login_manager.login_view = "main.login"
login_manager.login_message_category = "warning"


def _apply_security_headers(app: Flask, response):
    """Attach baseline browser security controls to every response."""
    if not app.config.get("SECURITY_HEADERS_ENABLED", True):
        return response

    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault(
        "Referrer-Policy",
        app.config.get("REFERRER_POLICY", "strict-origin-when-cross-origin"),
    )
    response.headers.setdefault(
        "Permissions-Policy",
        app.config.get(
            "PERMISSIONS_POLICY",
            "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
        ),
    )
    response.headers.setdefault(
        "Content-Security-Policy",
        app.config.get("CONTENT_SECURITY_POLICY", "default-src 'self'"),
    )
    response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
    response.headers.setdefault("X-Permitted-Cross-Domain-Policies", "none")

    if app.config.get("HSTS_ENABLED", False):
        max_age = int(app.config.get("HSTS_MAX_AGE", 31536000))
        response.headers.setdefault(
            "Strict-Transport-Security",
            f"max-age={max_age}; includeSubDomains",
        )

    if response.mimetype == "text/html":
        response.headers.setdefault("Cache-Control", "no-store")

    return response


def create_app(config_class=Config):
    """Create and configure the Sentrix Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(account_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(settings_page)
    app.register_blueprint(upload_bp)
    app.register_blueprint(main)

    @app.context_processor
    def inject_authenticated_metrics():
        """Expose user-scoped project, analysis and report totals to templates."""
        if not current_user.is_authenticated:
            return {
                "total_projects": 0,
                "total_analyses": 0,
                "total_reports": 0,
            }

        user_id = current_user.id
        return {
            "total_projects": Project.query.filter_by(user_id=user_id).count(),
            "total_analyses": Analysis.query.filter_by(user_id=user_id).count(),
            "total_reports": Analysis.query.filter(
                Analysis.user_id == user_id,
                Analysis.report_path.isnot(None),
            ).count(),
        }

    @app.after_request
    def apply_sentrix_response_policies(response):
        if response.mimetype == "text/html" and not response.direct_passthrough:
            body = response.get_data(as_text=True)
            body = body.replace("CodeSentinel AI", "Sentrix")
            body = body.replace("CodeSentinel", "Sentrix")
            response.set_data(body)
            response.headers["Content-Length"] = len(response.get_data())

        return _apply_security_headers(app, response)

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("403.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        db.session.rollback()
        return render_template("500.html"), 500

    with app.app_context():
        if app.config.get("DATABASE_AUTO_CREATE", True):
            db.create_all()

    return app


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


app = create_app()


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "0").lower() in {"1", "true", "yes", "on"}
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5000"))
    app.run(host=host, port=port, debug=debug)
