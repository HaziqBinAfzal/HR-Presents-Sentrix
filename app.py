import os
from datetime import datetime, timezone

from flask import Flask, render_template
from flask_login import LoginManager

from analyzer.routes.main import main
from brand import BRAND
from config import Config
from database import db
from extensions import mail
from helpers.schema_compat import apply_additive_schema_compatibility
from models import User


login_manager = LoginManager()
login_manager.login_view = "main.login"
login_manager.login_message_category = "warning"


def create_app(config_object=Config):
    """Application factory for Sentrix."""
    app = Flask(__name__)
    app.config.from_object(config_object)

    config_object.ensure_directories()
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    app.register_blueprint(main)

    @app.context_processor
    def inject_brand_context():
        return {
            "brand": BRAND,
            "current_year": datetime.now(timezone.utc).year,
        }

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
        # Retained for compatibility with the current project. Production
        # deployments should run managed Flask-Migrate/Alembic migrations.
        db.create_all()
        apply_additive_schema_compatibility()

    return app


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


app = create_app()


if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )
