import csv
import io
import json
import os

from flask import Blueprint, Response, abort, render_template, send_file
from flask_login import current_user, login_required

from models import Analysis, Project


artifacts = Blueprint("artifacts", __name__)


def _owned_analysis_or_404(analysis_id):
    return Analysis.query.filter_by(
        id=analysis_id,
        user_id=current_user.id,
    ).first_or_404()


def _analysis_payload(analysis):
    project = analysis.project
    return {
        "analysis_id": analysis.id,
        "project_id": project.project_id if project else None,
        "project_name": project.project_name if project else None,
        "filename": analysis.filename,
        "language": analysis.language,
        "status": analysis.status,
        "overall_score": analysis.overall_score,
        "pylint_score": analysis.pylint_score,
        "security_count": analysis.security_count,
        "issues_count": analysis.issues_count,
        "complexity": analysis.complexity,
        "formatting_status": analysis.formatting_status,
        "analysis_duration": analysis.analysis_duration,
        "total_files": analysis.total_files,
        "total_lines": analysis.total_lines,
        "functions_count": analysis.functions_count,
        "classes_count": analysis.classes_count,
        "comments_count": analysis.comments_count,
        "blank_lines": analysis.blank_lines,
        "ai_summary": analysis.ai_summary,
        "recommendations": analysis.recommendations,
        "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
    }


@artifacts.route("/projects/<string:project_id>")
@login_required
def project_history(project_id):
    project = Project.query.filter_by(
        project_id=project_id,
        user_id=current_user.id,
    ).first_or_404()

    analyses = (
        Analysis.query
        .filter_by(project_id=project.id, user_id=current_user.id)
        .order_by(Analysis.created_at.desc())
        .all()
    )

    return render_template(
        "project_history.html",
        project=project,
        analyses=analyses,
    )


@artifacts.route("/reports/<int:analysis_id>/download")
@login_required
def download_report(analysis_id):
    analysis = _owned_analysis_or_404(analysis_id)

    if not analysis.report_path:
        abort(404, description="No report has been generated for this analysis.")

    report_path = os.path.abspath(analysis.report_path)
    if not os.path.isfile(report_path):
        abort(404, description="The report file is unavailable.")

    return send_file(
        report_path,
        as_attachment=True,
        download_name=os.path.basename(report_path),
    )


@artifacts.route("/analyses/<int:analysis_id>/export.json")
@login_required
def export_analysis_json(analysis_id):
    analysis = _owned_analysis_or_404(analysis_id)
    payload = json.dumps(_analysis_payload(analysis), indent=2, ensure_ascii=False)

    return Response(
        payload,
        mimetype="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=sentrix-analysis-{analysis.id}.json"
        },
    )


@artifacts.route("/analyses/<int:analysis_id>/export.csv")
@login_required
def export_analysis_csv(analysis_id):
    analysis = _owned_analysis_or_404(analysis_id)
    payload = _analysis_payload(analysis)

    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(["field", "value"])
    for key, value in payload.items():
        writer.writerow([key, "" if value is None else value])

    return Response(
        stream.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=sentrix-analysis-{analysis.id}.csv"
        },
    )
