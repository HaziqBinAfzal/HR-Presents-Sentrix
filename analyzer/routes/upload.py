import os

from flask import Blueprint, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from database import db
from forms import UploadForm
from helpers.analysis_service import run_project_analysis
from helpers.upload_service import (
    build_metadata,
    create_project_workspace,
    generate_project_id,
    generate_unique_filename,
    validate_upload,
)
from models import Analysis, Project
from settings_models import UserSettings


upload_bp = Blueprint("upload_page", __name__)


def _format_bytes(value):
    value = int(value or 0)
    units = ["B", "KB", "MB", "GB"]
    size = float(value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.2f} {unit}"
        size /= 1024
    return "0 B"


@upload_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    form = UploadForm()
    preferences = UserSettings.for_user(current_user.id)

    total_projects = Project.query.filter_by(user_id=current_user.id).count()
    total_analyses = Analysis.query.filter_by(user_id=current_user.id).count()
    total_reports = Analysis.query.filter(
        Analysis.user_id == current_user.id,
        Analysis.report_path.isnot(None),
    ).count()
    storage_size = (
        db.session.query(db.func.sum(Project.file_size))
        .filter_by(user_id=current_user.id)
        .scalar()
        or 0
    )

    recent_analyses = (
        Analysis.query.filter_by(user_id=current_user.id)
        .order_by(Analysis.created_at.desc())
        .limit(5)
        .all()
    )

    recent_projects = (
        Project.query.filter_by(user_id=current_user.id)
        .order_by(Project.upload_date.desc())
        .limit(5)
        .all()
    )

    context = {
        "form": form,
        "preferences": preferences,
        "total_projects": total_projects,
        "total_analyses": total_analyses,
        "total_reports": total_reports,
        "storage_used": _format_bytes(storage_size),
        "recent_analyses": recent_analyses,
        "recent_projects": recent_projects,
        "max_upload_mb": int(current_app.config.get("MAX_CONTENT_LENGTH", 100 * 1024 * 1024) / (1024 * 1024)),
    }

    if not form.validate_on_submit():
        return render_template("upload.html", **context)

    uploaded_file = form.file.data
    is_valid, message = validate_upload(uploaded_file)
    if not is_valid:
        flash(message, "danger")
        return render_template("upload.html", **context)

    project_id = generate_project_id()
    workspace = create_project_workspace(
        current_app.config["PROJECT_FOLDER"],
        project_id,
    )
    stored_filename = generate_unique_filename(uploaded_file.filename)
    source_path = os.path.join(workspace["source"], stored_filename)

    try:
        uploaded_file.save(source_path)
        metadata = build_metadata(uploaded_file, stored_filename=stored_filename)

        submitted_name = (form.project_name.data or "").strip()
        project = Project(
            project_id=project_id,
            project_name=submitted_name or metadata["project_name"],
            original_filename=metadata["original_filename"],
            stored_filename=stored_filename,
            file_type=metadata["extension"],
            file_size=metadata["size"],
            project_path=workspace["root"],
            user_id=current_user.id,
        )
        db.session.add(project)
        db.session.commit()

        if not preferences.auto_run_analysis:
            flash(
                "Project uploaded successfully. Automatic analysis is disabled in Settings.",
                "success",
            )
            return redirect(url_for("main.history"))

        analysis_result = run_project_analysis(project, current_user)

        if preferences.auto_delete_archive and os.path.isfile(source_path):
            os.remove(source_path)

        flash("Project uploaded and analyzed successfully.", "success")
        return redirect(
            url_for(
                "main.results",
                analysis_id=analysis_result["analysis_id"],
            )
        )

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Sentrix project upload failed.")
        flash(
            "Sentrix could not process this project. Check the archive and try again.",
            "danger",
        )
        return redirect(url_for("upload_page.upload"))
