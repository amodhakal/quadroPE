import pytest


@pytest.fixture()
def app():
    """Create a Flask app instance with the real database for testing."""
    from app import create_app

    app = create_app()
    app.config["TESTING"] = True
    yield app


@pytest.fixture()
def client(app):
    """A Flask test client for sending HTTP requests."""
    return app.test_client()
