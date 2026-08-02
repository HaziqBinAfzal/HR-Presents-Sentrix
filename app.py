import os

from extensions import mail
from flask import Flask, render_template
from models import User
from flask_login import LoginManager
from flask_migrate import Migrate
from analyzer.routes.main import main
from config import Config
from database import db


login_manager = LoginManager()
login_manager.login_view = "main.login"
login_manager.login_message_category = "warning"


def create_app():
    app = Flask(__name__)

    # Load application configuration
    app.config.from_object(Config)
    mail.init_app(app)

    app.config.setdefault("SESSION_COOKIE_HTTPONLY", True)
    app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")

    # Initialize database
    db.init_app(app)


    migrate = Migrate(app, db)

    # Initialize Flask-Login
    login_manager.init_app(app)

    # Register routes
    app.register_blueprint(main)

    # --------------------------------------------------
    # Error Handlers
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Create Required Directories + Database
    # --------------------------------------------------

    with app.app_context():

        # Create database tables
        db.create_all()

    return app


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
