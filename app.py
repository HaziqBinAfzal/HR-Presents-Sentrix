from flask import Flask
from config import Config
from database import db


app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)


@app.route("/")
def home():
    return """
    <h1>Welcome to CodeSentinel AI</h1>
    <h3>Backend is Working Successfully</h3>
    """


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
