from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify
from sqlalchemy import text

from database import db


health = Blueprint("health", __name__, url_prefix="/health")


@health.get("/live")
def liveness():
    return jsonify(
        status="ok",
        service="sentrix",
        check="liveness",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@health.get("/ready")
def readiness():
    try:
        db.session.execute(text("SELECT 1"))
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Sentrix readiness database check failed.")
        return jsonify(
            status="unavailable",
            service="sentrix",
            check="readiness",
            database="unavailable",
        ), 503

    return jsonify(
        status="ok",
        service="sentrix",
        check="readiness",
        database="available",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
