import os

from database import db
from extensions import mail, migrate
from flask import Flask, render_template, request
from flask_login import LoginManager

from analyzer.routes.auth import auth
from analyzer.routes.exports import exports
from analyzer.routes.health import health
from analyzer.routes.main import main
from config import Config
from forms import LoginForm, RegisterForm
from helpers.branding import register_branding
from helpers.security import register_security_headers
from models import User


login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    app.config.setdefault("SESSION_COOKIE_HTTPONLY", True)
    app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(exports)
    app.register_blueprint(health)
    register_branding(app)
    register_security_headers(app)

    @app.context_processor
    def authentication_forms():
        if request.endpoint == "auth.login":
            return {"form": LoginForm()}
        if request.endpoint == "auth.register":
            return {"form": RegisterForm()}
        return {}

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("403.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        db.session.rollback()
        app.logger.exception("Unhandled server error", exc_info=error)
        return render_template("500.html"), 500

    with app.app_context():
        for config_key in (
            "UPLOAD_FOLDER",
            "TEMP_FOLDER",
            "PROJECT_FOLDER",
            "REPORT_FOLDER",
            "CORRECTED_FOLDER",
            "DIFF_FOLDER",
        ):
            folder = app.config.get(config_key)
            if folder:
                os.makedirs(folder, exist_ok=True)

    return app


@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None


app = create_app()


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
