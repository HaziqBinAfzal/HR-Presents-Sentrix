import csv
import io
import os
import uuid

from flask import abort, current_app, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from database import db
from models import Analysis, Project, Review, User


ALLOWED_PROFILE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def _owned_analysis_or_404(analysis_id):
    return Analysis.query.filter_by(
        id=analysis_id,
        user_id=current_user.id,
    ).first_or_404()


def dashboard():
    total_projects = Project.query.filter_by(user_id=current_user.id).count()
    total_analyses = Analysis.query.filter_by(user_id=current_user.id).count()
    total_reports = Analysis.query.filter(
        Analysis.user_id == current_user.id,
        Analysis.report_path.isnot(None),
    ).count()

    security_issues = (
        db.session.query(db.func.sum(Analysis.security_count))
        .filter_by(user_id=current_user.id)
        .scalar()
        or 0
    )
    latest_analysis = (
        Analysis.query.filter_by(user_id=current_user.id)
        .order_by(Analysis.created_at.desc())
        .first()
    )
    recent_analyses = (
        Analysis.query.filter_by(user_id=current_user.id)
        .order_by(Analysis.created_at.desc())
        .limit(5)
        .all()
    )

    overall_score = round(
        db.session.query(db.func.avg(Analysis.overall_score))
        .filter_by(user_id=current_user.id)
        .scalar()
        or 0,
        1,
    )
    quality_score = round(
        db.session.query(db.func.avg(Analysis.pylint_score))
        .filter_by(user_id=current_user.id)
        .scalar()
        or 0,
        1,
    )
    total_size = (
        db.session.query(db.func.sum(Project.file_size))
        .filter_by(user_id=current_user.id)
        .scalar()
        or 0
    )

    chart_analyses = list(reversed(recent_analyses))
    quality_chart = {
        "labels": [item.created_at.strftime("%d %b") for item in chart_analyses],
        "datasets": [{
            "label": "Overall Score",
            "data": [item.overall_score for item in chart_analyses],
            "fill": False,
        }],
    }
    secure_projects = Analysis.query.filter(
        Analysis.user_id == current_user.id,
        Analysis.security_count == 0,
    ).count()
    projects_with_issues = Analysis.query.filter(
        Analysis.user_id == current_user.id,
        Analysis.security_count > 0,
    ).count()
    security_chart = {
        "labels": ["Secure Projects", "Projects with Issues"],
        "datasets": [{"data": [secure_projects, projects_with_issues]}],
    }
    recent_activities = [{
        "title": item.filename,
        "project": item.filename,
        "status": item.status,
        "score": item.overall_score,
        "date": item.created_at.strftime("%d %b %Y"),
    } for item in recent_analyses]

    return render_template(
        "dashboard.html",
        total_projects=total_projects,
        total_analyses=total_analyses,
        total_reports=total_reports,
        latest_stats=latest_analysis,
        security_issues=security_issues,
        overall_score=overall_score,
        quality_score=quality_score,
        storage_used=f"{round(total_size / (1024 * 1024), 2)} MB",
        recent_analyses=recent_analyses,
        security_score=100,
        maintainability_score=100,
        ai_score=100,
        quality_chart=quality_chart,
        security_chart=security_chart,
        language_chart=None,
        recent_activities=recent_activities,
        ai_insight=(
            latest_analysis.ai_summary
            if latest_analysis and latest_analysis.ai_summary
            else "Upload a project to receive AI insights."
        ),
    )


def profile():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        if not username or not email:
            flash("Username and email are required.", "danger")
            return redirect(url_for("main.profile"))

        duplicate = User.query.filter(
            User.id != current_user.id,
            db.or_(User.username == username, User.email == email),
        ).first()
        if duplicate:
            flash("That username or email is already in use.", "danger")
            return redirect(url_for("main.profile"))

        current_user.username = username
        current_user.email = email
        current_user.full_name = request.form.get("full_name", "").strip()
        current_user.organization = request.form.get("organization", "").strip()
        current_user.bio = request.form.get("bio", "").strip()

        picture = request.files.get("profile_picture")
        if picture and picture.filename:
            original_name = secure_filename(picture.filename)
            if "." not in original_name:
                flash("Invalid profile image.", "danger")
                return redirect(url_for("main.profile"))
            extension = original_name.rsplit(".", 1)[1].lower()
            if extension not in ALLOWED_PROFILE_EXTENSIONS:
                flash("Use PNG, JPG, JPEG, GIF, or WEBP.", "danger")
                return redirect(url_for("main.profile"))

            profile_folder = os.path.join(
                current_app.root_path,
                current_app.config["UPLOAD_FOLDER"],
                "profile_pics",
            )
            os.makedirs(profile_folder, exist_ok=True)
            filename = f"user_{current_user.id}_{uuid.uuid4().hex}.{extension}"
            picture.save(os.path.join(profile_folder, filename))
            current_user.profile_picture = filename

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("main.profile"))

    recent_projects = (
        Project.query.filter_by(user_id=current_user.id)
        .order_by(Project.upload_date.desc())
        .limit(5)
        .all()
    )
    return render_template(
        "profile.html",
        total_projects=Project.query.filter_by(user_id=current_user.id).count(),
        total_analyses=Analysis.query.filter_by(user_id=current_user.id).count(),
        total_reviews=Review.query.filter_by(user_id=current_user.id).count(),
        recent_projects=recent_projects,
    )


def reports():
    analyses = (
        Analysis.query.filter_by(user_id=current_user.id)
        .order_by(Analysis.created_at.desc())
        .all()
    )
    return render_template("reports.html", analyses=analyses)


def download_report(analysis_id):
    analysis = _owned_analysis_or_404(analysis_id)
    if not analysis.report_path:
        abort(404)
    report_path = os.path.abspath(analysis.report_path)
    if not os.path.isfile(report_path):
        abort(404)
    return send_file(
        report_path,
        as_attachment=True,
        download_name=os.path.basename(report_path),
    )


def export_history_csv():
    analyses = (
        Analysis.query.filter_by(user_id=current_user.id)
        .order_by(Analysis.created_at.desc())
        .all()
    )
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Analysis ID", "File", "Language", "Overall Score", "Pylint Score",
        "Security Issues", "Complexity", "Status", "Created At",
    ])
    for item in analyses:
        writer.writerow([
            item.id, item.filename, item.language, item.overall_score,
            item.pylint_score, item.security_count, item.complexity,
            item.status, item.created_at.isoformat(),
        ])
    data = io.BytesIO(output.getvalue().encode("utf-8-sig"))
    data.seek(0)
    return send_file(
        data,
        mimetype="text/csv",
        as_attachment=True,
        download_name="sentrix-analysis-history.csv",
    )


def install_production_routes(blueprint):
    # Replace broken legacy handlers before the blueprint is registered.
    blueprint.view_functions["dashboard"] = login_required(dashboard)
    blueprint.view_functions["profile"] = login_required(profile)

    blueprint.add_url_rule(
        "/reports",
        endpoint="reports",
        view_func=login_required(reports),
        methods=["GET"],
    )
    blueprint.add_url_rule(
        "/reports/<int:analysis_id>/download",
        endpoint="download_report",
        view_func=login_required(download_report),
        methods=["GET"],
    )
    blueprint.add_url_rule(
        "/history/export.csv",
        endpoint="export_history_csv",
        view_func=login_required(export_history_csv),
        methods=["GET"],
    )
