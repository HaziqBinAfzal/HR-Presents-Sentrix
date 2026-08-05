from tests.conftest import login


def test_public_html_responses_include_security_headers(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "camera=()" in response.headers["Permissions-Policy"]
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]


def test_hsts_can_be_forced_in_production_configuration(client, app):
    app.config["FORCE_HTTPS_HEADERS"] = True
    response = client.get("/")

    assert response.headers["Strict-Transport-Security"].startswith("max-age=31536000")


def test_export_responses_are_not_cached(client, analysis_record):
    _, analysis_id = analysis_record
    login(client, "owner@example.com")

    csv_response = client.get("/exports/history.csv")
    json_response = client.get(f"/exports/analysis/{analysis_id}.json")

    assert csv_response.headers["Cache-Control"] == "no-store"
    assert json_response.headers["Cache-Control"] == "no-store"


def test_session_cookie_security_defaults(app):
    assert app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"
    assert app.config["REMEMBER_COOKIE_HTTPONLY"] is True
    assert app.config["REMEMBER_COOKIE_SAMESITE"] == "Lax"
