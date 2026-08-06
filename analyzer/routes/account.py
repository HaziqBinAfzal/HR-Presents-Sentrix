"""Secure account-management routes for Sentrix."""

import shutil
from pathlib import Path

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, logout_user

from database import db
from forms import ChangePasswordForm
from models import Analysis, Project, Review, User
from settings_models import UserSettings


account_bp = Blueprint("account", __name__)


def _remove_path(path):
    if not path:
        return

    try:
        candidate = Path(path)
        if candidate.is_dir():
            shutil.rmtree(candidate, ignore_errors=True)
        elif candidate.is_file():
            candidate.unlink(missing_ok=True)
    except (OSError, TypeError, ValueError):
        current_app.logger.exception("Unable to remove account-owned path: %s", path)


@account_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            form.current_password.errors.append("Your current password is incorrect.")
        elif current_user.check_password(form.new_password.data):
            form.new_password.errors.append("Your new password must be different.")
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            logout_user()
            flash("Password changed successfully. Please sign in again.", "success")
            return redirect(url_for("main.login"))

    return render_template("change_password.html", form=form)


@account_bp.route("/account/delete", methods=["GET", "POST"])
@login_required
def delete_account():
    if request.method == "GET":
        return render_template("delete_account.html")

    password = request.form.get("password", "")
    confirmation = request.form.get("confirmation", "").strip()

    if not current_user.check_password(password):
        flash("Your password is incorrect.", "danger")
        return render_template("delete_account.html"), 400

    if confirmation != "DELETE":
        flash('Type "DELETE" exactly to confirm permanent account removal.', "danger")
        return render_template("delete_account.html"), 400

    user_id = current_user.id
    user = db.session.get(User, user_id)
    projects = Project.query.filter_by(user_id=user_id).all()
    analyses = Analysis.query.filter_by(user_id=user_id).all()

    for analysis in analyses:
        _remove_path(analysis.report_path)

    for project in projects:
        _remove_path(project.project_path)

    if user and user.profile_picture and user.profile_picture != "default.png":
        upload_root = Path(current_app.config["UPLOAD_FOLDER"])
        _remove_path(upload_root / "profile_pics" / user.profile_picture)

    try:
        UserSettings.query.filter_by(user_id=user_id).delete(synchronize_session=False)
        Review.query.filter_by(user_id=user_id).delete(synchronize_session=False)
        Analysis.query.filter_by(user_id=user_id).delete(synchronize_session=False)
        Project.query.filter_by(user_id=user_id).delete(synchronize_session=False)

        logout_user()
        if user is not None:
            db.session.delete(user)
        db.session.commit()

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to delete Sentrix account %s", user_id)
        flash("Your account could not be deleted. Please try again.", "danger")
        return redirect(url_for("account.delete_account"))

    flash("Your Sentrix account and associated data were permanently deleted.", "success")
    return redirect(url_for("main.home"))
