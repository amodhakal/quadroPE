"""Tests for the Flask application factory and route registration."""

from flask import Flask


def test_create_app_returns_flask_instance(app):
    assert isinstance(app, Flask)


def test_app_has_testing_config(app):
    assert app.config["TESTING"] is True


def test_app_registers_health_route(app):
    rules = [rule.rule for rule in app.url_map.iter_rules()]
    assert "/health" in rules


def test_app_registers_user_routes(app):
    rules = [rule.rule for rule in app.url_map.iter_rules()]
    assert "/users" in rules
    assert "/users/<int:user_id>" in rules
    assert "/users/bulk" in rules


def test_app_registers_url_routes(app):
    rules = [rule.rule for rule in app.url_map.iter_rules()]
    assert "/urls" in rules
    assert "/urls/<int:url_id>" in rules


def test_app_registers_event_routes(app):
    rules = [rule.rule for rule in app.url_map.iter_rules()]
    assert "/events" in rules


def test_unknown_route_returns_404(client):
    response = client.get("/nonexistent")
    assert response.status_code == 404


def test_404_response_is_json(client):
    response = client.get("/nonexistent")
    assert response.content_type == "application/json"
    data = response.get_json()
    assert "error" in data
