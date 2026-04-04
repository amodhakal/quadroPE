"""Tests for the /logs endpoint."""

import pytest

from app.log_store import log_records


@pytest.fixture(autouse=True)
def clear_log_records():
    """Clear the in-memory log buffer before and after every test."""
    log_records.clear()
    yield
    log_records.clear()


def test_logs_returns_200(client):
    response = client.get("/logs")
    assert response.status_code == 200


def test_logs_returns_json(client):
    response = client.get("/logs")
    assert response.content_type == "application/json"


def test_logs_response_has_logs_key(client):
    response = client.get("/logs")
    data = response.get_json()
    assert "logs" in data


def test_logs_empty_when_no_records(client):
    response = client.get("/logs")
    data = response.get_json()
    assert data["logs"] == []


def test_logs_returns_captured_records(client):
    log_records.append({"level": "INFO", "message": "hello world"})
    response = client.get("/logs")
    data = response.get_json()
    assert len(data["logs"]) == 1
    assert data["logs"][0]["message"] == "hello world"


def test_logs_caps_at_50_most_recent_records(client):
    for i in range(75):
        log_records.append({"level": "INFO", "message": f"message {i}"})

    response = client.get("/logs")
    data = response.get_json()

    # Only the last 50 records should be returned.
    assert len(data["logs"]) == 50
    assert data["logs"][0]["message"] == "message 25"
    assert data["logs"][-1]["message"] == "message 74"


def test_logs_returns_list_under_logs_key(client):
    response = client.get("/logs")
    data = response.get_json()
    assert isinstance(data["logs"], list)


def test_logs_only_allows_get(client):
    """POST, PUT, DELETE should not be allowed on /logs."""
    for method in [client.post, client.put, client.delete]:
        response = method("/logs")
        assert response.status_code == 405
