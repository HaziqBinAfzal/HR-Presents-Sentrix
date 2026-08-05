import os

from flask import Flask, render_template
from flask_login import LoginManager

from analyzer.routes.main import main
from analyzer.routes.settings import settings_bp
from config import Config
from database import db
from extensions import mail, csrf
from models import User
from settings_models import UserSettings  # noqa: F401 - registers the model before create_all


login_manager = LoginManager()
login_manager.login_view = "main.login"
login_manager.login_message_category = "warning"


def create_app(config_class=Config):
    """Create and configure the Sentrix Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    # Register the dynamic settings blueprint first so /settings resolves to it.
    app.register_blueprint(settings_bp)
    app.register_blueprint(main)

    @app.after_request
    def apply_sentrix_branding(response):
        """Remove legacy product naming from rendered HTML responses."""
        if response.mimetype == "text/html" and not response.direct_passthrough:
            body = response.get_data(as_text=True)
            body = body.replace("CodeSentinel AI", "Sentrix")
            body = body.replace("CodeSentinel", "Sentrix")
            response.set_data(body)
            response.headers["Content-Length"] = len(response.get_data())
        return response

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
