from flask import Blueprint, redirect, url_for
from flask_login import login_required


settings_page = Blueprint("settings_page", __name__)


@settings_page.get("/settings-link")
@login_required
def settings():
    """Compatibility endpoint for templates linking to dynamic settings."""
    return redirect(url_for("settings_v2.settings_page"))
