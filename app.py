from flask import Flask

from config import Config
from database import db

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)

import models


@app.route("/")
def home():
    return """
    <h1>CodeSentinel AI</h1>
    <h3>Database Connected Successfully</h3>
    """


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
