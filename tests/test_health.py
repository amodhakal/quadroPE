"""Tests for the /health endpoint."""


def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_json(client):
    response = client.get("/health")
    assert response.content_type == "application/json"


def test_health_body_contains_status_ok(client):
    response = client.get("/health")
    data = response.get_json()
    assert data == {"status": "ok"}


def test_health_status_field_is_ok(client):
    response = client.get("/health")
    data = response.get_json()
    assert "status" in data
    assert data["status"] == "ok"


def test_health_only_allows_get(client):
    """POST, PUT, DELETE should not be allowed on /health."""
    for method in [client.post, client.put, client.delete]:
        response = method("/health")
        assert response.status_code == 405
