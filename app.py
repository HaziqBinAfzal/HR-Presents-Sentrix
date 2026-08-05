from datetime import datetime

from extensions import mail
from flask import Flask, render_template
from flask_login import LoginManager

from analyzer.routes.main import main
from config import Config
from database import db
from models import User


login_manager = LoginManager()
login_manager.login_view = "main.login"
login_manager.login_message_category = "warning"


@main.route("/documentation")
def documentation():
    """Render the public Sentrix documentation center."""
    return render_template("documentation.html")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.config.setdefault("SESSION_COOKIE_HTTPONLY", True)
    app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")
    app.config.setdefault("SESSION_COOKIE_SECURE", not app.debug)

    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    app.register_blueprint(main)

    @app.context_processor
    def inject_brand_context():
        return {
            "brand_name": "Sentrix",
            "brand_subtitle": "Presented by HR-Presents",
            "support_email": "supportsentrix@gmail.com",
            "current_year": datetime.utcnow().year,
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
        db.create_all()

    return app


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


app = create_app()


if __name__ == "__main__":
    app.run(debug=False)
