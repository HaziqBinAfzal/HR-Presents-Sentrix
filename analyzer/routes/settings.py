import os
import shutil
import tempfile
from pathlib import Path

from flask import Blueprint, current_app, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required

from database import db
from models import Analysis, Project, Review
from settings_models import UserSettings


settings_bp = Blueprint("settings_v2", __name__)


def _format_bytes(value):
    value = int(value or 0)
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.2f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{value} B"


def _user_projects():
    return Project.query.filter_by(user_id=current_user.id)


def _user_analyses():
    return Analysis.query.filter_by(user_id=current_user.id)


def _safe_remove(path):
    try:
        candidate = Path(path)
        if candidate.is_dir():
            shutil.rmtree(candidate, ignore_errors=True)
        elif candidate.is_file():
            candidate.unlink(missing_ok=True)
        return True
    except (OSError, TypeError, ValueError):
        return False


@settings_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings_page():
    user_settings = UserSettings.for_user(current_user.id)

    if request.method == "POST":
        section = request.form.get("section", "preferences")

        if section == "preferences":
            user_settings.analysis_mode = request.form.get("analysis_mode", "standard")
            user_settings.report_format = request.form.get("report_format", "html")
            user_settings.enable_black = "enable_black" in request.form
            user_settings.enable_bandit = "enable_bandit" in request.form
            user_settings.enable_radon = "enable_radon" in request.form
            user_settings.enable_pylint = "enable_pylint" in request.form
            user_settings.enable_ai = "enable_ai" in request.form
            user_settings.auto_run_analysis = "auto_run_analysis" in request.form
            user_settings.auto_generate_report = "auto_generate_report" in request.form
            user_settings.auto_delete_archive = "auto_delete_archive" in request.form
            user_settings.save_analysis_history = "save_analysis_history" in request.form
            message = "Analysis preferences saved."

        elif section == "notifications":
            user_settings.notify_complete = "notify_complete" in request.form
            user_settings.notify_failed = "notify_failed" in request.form
            user_settings.notify_security = "notify_security" in request.form
            user_settings.weekly_summary = "weekly_summary" in request.form
            message = "Notification preferences saved."

        else:
            flash("Unknown settings section.", "danger")
            return redirect(url_for("settings_v2.settings_page"))

        db.session.commit()
        flash(message, "success")
        return redirect(url_for("settings_v2.settings_page"))

    projects = _user_projects().order_by(Project.upload_date.desc()).all()
    analyses = _user_analyses().order_by(Analysis.created_at.desc()).all()
    reports = [item for item in analyses if item.report_path]

    storage_bytes = sum(project.file_size or 0 for project in projects)
    largest_project = max(projects, key=lambda item: item.file_size or 0, default=None)
    average_project_bytes = storage_bytes / len(projects) if projects else 0
    total_security_issues = sum(item.security_count or 0 for item in analyses)
    average_score = (
        round(sum(item.overall_score or 0 for item in analyses) / len(analyses), 1)
        if analyses else 0
    )

    existing_reports = [item for item in reports if item.report_path and Path(item.report_path).is_file()]

    return render_template(
        "settings.html",
        user_settings=user_settings,
        total_projects=len(projects),
        total_analyses=len(analyses),
        total_reports=len(existing_reports),
        total_reviews=Review.query.filter_by(user_id=current_user.id).count(),
        storage_used=_format_bytes(storage_bytes),
        storage_bytes=storage_bytes,
        largest_project=largest_project,
        average_project_size=_format_bytes(average_project_bytes),
        latest_project=projects[0] if projects else None,
        latest_analysis=analyses[0] if analyses else None,
        latest_report=existing_reports[0] if existing_reports else None,
        total_security_issues=total_security_issues,
        average_score=average_score,
        reports=existing_reports,
        sentrix_version=current_app.config.get("APP_VERSION", "1.0.0"),
    )


@settings_bp.post("/settings/clear-temporary-files")
@login_required
def clear_temporary_files():
    removed = 0
    temp_roots = {
        Path(tempfile.gettempdir()),
        Path(current_app.root_path) / "uploads" / "temp",
        Path(current_app.root_path) / "tmp",
    }

    for root in temp_roots:
        if not root.exists() or not root.is_dir():
            continue
        for candidate in root.iterdir():
            if candidate.name.startswith(("sentrix_", "codesentinel_")):
                if _safe_remove(candidate):
                    removed += 1

    flash(f"Removed {removed} temporary item(s).", "success")
    return redirect(url_for("settings_v2.settings_page"))


@settings_bp.post("/settings/delete-reports")
@login_required
def delete_all_reports():
    analyses = _user_analyses().filter(Analysis.report_path.isnot(None)).all()
    removed = 0
    for analysis in analyses:
        if analysis.report_path and _safe_remove(analysis.report_path):
            removed += 1
        analysis.report_path = None
    db.session.commit()
    flash(f"Deleted {removed} generated report file(s).", "success")
    return redirect(url_for("settings_v2.settings_page"))


@settings_bp.get("/settings/reports")
@login_required
def report_library():
    reports = (
        _user_analyses()
        .filter(Analysis.report_path.isnot(None))
        .order_by(Analysis.created_at.desc())
        .all()
    )
    reports = [item for item in reports if item.report_path and Path(item.report_path).is_file()]
    return render_template("report_library.html", reports=reports)


@settings_bp.get("/settings/reports/<int:analysis_id>/download")
@login_required
def download_settings_report(analysis_id):
    analysis = _user_analyses().filter_by(id=analysis_id).first_or_404()
    if not analysis.report_path or not Path(analysis.report_path).is_file():
        flash("The report file is unavailable.", "danger")
        return redirect(url_for("settings_v2.report_library"))
    return send_file(
        analysis.report_path,
        as_attachment=True,
        download_name=f"{analysis.filename}_report.html",
        mimetype="text/html",
    )
