from flask import Blueprint, render_template, redirect, url_for

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("home.html")


@main.route("/login")
def login():
    return render_template("login.html")


@main.route("/register")
def register():
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
