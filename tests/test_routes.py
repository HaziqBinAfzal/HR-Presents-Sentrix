from database import db
from models import Analysis
from tests.conftest import login


def test_public_pages_render(client):
    for path in ("/", "/about", "/contact", "/login", "/register"):
        response = client.get(path)
        assert response.status_code == 200


def test_private_pages_redirect_anonymous_users(client):
    for path in ("/dashboard", "/upload", "/history", "/profile", "/settings"):
        response = client.get(path)
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]


def test_login_and_dashboard(client, users):
    response = login(client, "owner@example.com")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")

    dashboard = client.get("/dashboard")
    assert dashboard.status_code == 200
    assert b"Sentrix" in dashboard.data


def test_results_are_owner_scoped(client, app, users, analysis_record):
    _, outsider_id = users
    _, analysis_id = analysis_record

    login(client, "outsider@example.com")
    response = client.get(f"/results/{analysis_id}")
    assert response.status_code == 302

    with app.app_context():
        assert db.session.get(Analysis, analysis_id).user_id != outsider_id


def test_owner_can_view_results(client, analysis_record):
    _, analysis_id = analysis_record
    login(client, "owner@example.com")
    response = client.get(f"/results/{analysis_id}")
    assert response.status_code == 200


def test_history_csv_export_requires_login(client):
    response = client.get("/exports/history.csv")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_owner_can_export_history_csv(client, analysis_record):
    login(client, "owner@example.com")
    response = client.get("/exports/history.csv")
    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert b"sample.py" in response.data
    assert response.headers["Cache-Control"] == "no-store"


def test_owner_can_export_analysis_json(client, analysis_record):
    _, analysis_id = analysis_record
    login(client, "owner@example.com")
    response = client.get(f"/exports/analysis/{analysis_id}.json")
    assert response.status_code == 200
    assert response.is_json
    payload = response.get_json()
    assert payload["analysis"]["id"] == analysis_id
    assert payload["analysis"]["filename"] == "sample.py"


def test_outsider_cannot_export_analysis(client, analysis_record):
    _, analysis_id = analysis_record
    login(client, "outsider@example.com")
    response = client.get(f"/exports/analysis/{analysis_id}.json")
    assert response.status_code == 404


def test_project_history_is_owner_scoped(client, analysis_record):
    project_uid, _ = analysis_record

    login(client, "outsider@example.com")
    denied = client.get(f"/projects/{project_uid}/history")
    assert denied.status_code == 404

    client.get("/logout")
    login(client, "owner@example.com")
    allowed = client.get(f"/projects/{project_uid}/history")
    assert allowed.status_code == 200
    assert b"Sample Project" in allowed.data
