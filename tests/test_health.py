def test_liveness_endpoint(client):
    response = client.get("/health/live")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"
    assert payload["service"] == "sentrix"
    assert payload["check"] == "liveness"


def test_readiness_endpoint(client):
    response = client.get("/health/ready")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"
    assert payload["database"] == "available"
