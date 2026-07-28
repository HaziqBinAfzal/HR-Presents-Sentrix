from flask import Flask
from analyzer.routes.main import main


def create_app():
    app = Flask(__name__)

    # Required for flash messages and sessions
    app.secret_key = "codesentinel-secret-key"

    # Register main blueprint
    app.register_blueprint(main)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
