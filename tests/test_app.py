"""Tests for the Flask application factory."""

from flask import Flask


def test_create_app_returns_flask_instance(app):
    assert isinstance(app, Flask)


def test_app_has_testing_config(app):
    assert app.config["TESTING"] is True


def test_app_registers_health_route(app):
    rules = [rule.rule for rule in app.url_map.iter_rules()]
    assert "/health" in rules


def test_app_health_rule_methods(app):
    """The /health route should accept GET and HEAD (HEAD is implicit in Flask)."""
    for rule in app.url_map.iter_rules():
        if rule.rule == "/health":
            assert "GET" in rule.methods
            break
    else:
        raise AssertionError("/health route not found")


def test_unknown_route_returns_404(client):
    response = client.get("/nonexistent")
    assert response.status_code == 404
