from flask import Blueprint, render_template, request, redirect, url_for, flash

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("home.html")


@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        print("Login attempt:", username)

        # Temporary login logic
        if username and password:
            flash("Login successful!", "success")
            return redirect(url_for("main.dashboard"))

        flash("Please enter username and password.", "error")

    return render_template("login.html")


@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        print("Registration:", username, email)

        # Temporary registration logic
        if username and email and password:
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("main.login"))

        flash("Please fill in all fields.", "error")

    return render_template("register.html")


@main.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@main.route("/upload")
def upload():
    return render_template("upload.html")


@main.route("/results")
def results():
    return render_template("results.html")


@main.route("/history")
def history():
    return render_template("history.html")


@main.route("/settings")
def settings():
    return render_template("settings.html")


@main.route("/profile")
def profile():
    return render_template("profile.html")


@main.route("/logout")
def logout():
    return redirect(url_for("main.home"))


@main.app_errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404
