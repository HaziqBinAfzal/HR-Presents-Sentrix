from flask import Blueprint, abort, jsonify, url_for
from flask_login import current_user, login_required

from background_models import AnalysisJob


analysis_jobs_bp = Blueprint("analysis_jobs", __name__)


@analysis_jobs_bp.get("/api/analysis-jobs/<int:job_id>")
@login_required
def analysis_job_status(job_id):
    job = AnalysisJob.query.filter_by(id=job_id, user_id=current_user.id).first()
    if job is None:
        abort(404)

    payload = job.as_dict()
    if job.analysis_id:
        payload["results_url"] = url_for(
            "main.results", analysis_id=job.analysis_id
        )
    else:
        payload["results_url"] = None
    return jsonify(payload)
