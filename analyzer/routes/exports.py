import csv
import io
import json
import os
from datetime import datetime

from flask import Blueprint, Response, abort, current_app, render_template, send_file
from flask_login import current_user, login_required

from models import Analysis, Project


exports = Blueprint("exports", __name__)


def _analysis_payload(analysis):
    return {
        "id": analysis.id,
        "project_id": analysis.project_id,
        "filename": analysis.filename,
        "language": analysis.language,
        "status": analysis.status,
        "overall_score": analysis.overall_score,
        "pylint_score": analysis.pylint_score,
        "security_count": analysis.security_count,
        "complexity": analysis.complexity,
        "issues_count": analysis.issues_count,
        "total_files": analysis.total_files,
        "total_lines": analysis.total_lines,
        "analysis_duration": analysis.analysis_duration,
        "ai_summary": analysis.ai_summary,
        "recommendations": analysis.recommendations,
        "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
        "report_available": bool(analysis.report_path),
    }


def _safe_download_name(filename, suffix):
    stem = os.path.splitext(os.path.basename(filename or "analysis"))[0]
    safe_stem = "".join(character for character in stem if character.isalnum() or character in ("-", "_"))
    return f"{safe_stem or 'analysis'}_{suffix}"


@exports.route("/projects/<string:project_uid>/history")
@login_required
def project_history(project_uid):
    project = Project.query.filter_by(
        project_id=project_uid,
        user_id=current_user.id,
    ).first_or_404()

    analyses = (
        Analysis.query.filter_by(
            project_id=project.id,
            user_id=current_user.id,
        )
        .order_by(Analysis.created_at.desc())
        .all()
    )

    return render_template(
        "project_history.html",
        project=project,
        analyses=analyses,
    )


@exports.route("/exports/history.csv")
@login_required
def export_history_csv():
    analyses = (
        Analysis.query.filter_by(user_id=current_user.id)
        .order_by(Analysis.created_at.desc())
        .all()
    )

    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow([
        "Analysis ID",
        "Project ID",
        "Filename",
        "Language",
        "Status",
        "Overall Score",
        "Pylint Score",
        "Security Issues",
        "Complexity",
        "Issue Count",
        "Total Files",
        "Total Lines",
        "Duration Seconds",
        "Created At",
        "Report Available",
    ])

    for analysis in analyses:
        writer.writerow([
            analysis.id,
            analysis.project_id,
            analysis.filename,
            analysis.language,
            analysis.status,
            analysis.overall_score,
            analysis.pylint_score,
            analysis.security_count,
            analysis.complexity,
            analysis.issues_count,
            analysis.total_files,
            analysis.total_lines,
            analysis.analysis_duration,
            analysis.created_at.isoformat() if analysis.created_at else "",
            "yes" if analysis.report_path else "no",
        ])

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=sentrix_history_{timestamp}.csv",
            "Cache-Control": "no-store",
        },
    )


@exports.route("/exports/analysis/<int:analysis_id>.json")
@login_required
def export_analysis_json(analysis_id):
    analysis = Analysis.query.filter_by(
        id=analysis_id,
        user_id=current_user.id,
    ).first_or_404()

    content = json.dumps(_analysis_payload(analysis), indent=2, ensure_ascii=False)
    return Response(
        content,
        mimetype="application/json",
        headers={
            "Content-Disposition": (
                "attachment; filename="
                f"{_safe_download_name(analysis.filename, 'analysis.json')}"
            ),
            "Cache-Control": "no-store",
        },
    )


@exports.route("/exports/report/<int:analysis_id>")
@login_required
def export_report(analysis_id):
    analysis = Analysis.query.filter_by(
        id=analysis_id,
        user_id=current_user.id,
    ).first_or_404()

    report_path = analysis.report_path
    if not report_path:
        abort(404)

    absolute_path = os.path.abspath(report_path)
    report_root = os.path.abspath(current_app.config["REPORT_FOLDER"])
    try:
        is_inside_report_root = os.path.commonpath([absolute_path, report_root]) == report_root
    except ValueError:
        is_inside_report_root = False

    if not is_inside_report_root:
        current_app.logger.warning(
            "Blocked report path outside configured report directory for analysis %s",
            analysis.id,
        )
        abort(403)

    if not os.path.isfile(absolute_path):
        abort(404)

    extension = os.path.splitext(absolute_path)[1].lower()
    mimetype = {
        ".html": "text/html",
        ".pdf": "application/pdf",
        ".json": "application/json",
    }.get(extension, "application/octet-stream")

    return send_file(
        absolute_path,
        as_attachment=True,
        download_name=_safe_download_name(analysis.filename, f"report{extension}"),
        mimetype=mimetype,
        conditional=True,
        max_age=0,
    )
