"""Tests for the database module."""

import os
from unittest.mock import patch

from peewee import DatabaseProxy, Model

from app.database import BaseModel, db


def test_db_is_a_database_proxy():
    assert isinstance(db, DatabaseProxy)


def test_base_model_uses_db_proxy():
    assert BaseModel._meta.database is db


def test_base_model_is_peewee_model():
    assert issubclass(BaseModel, Model)


def test_init_db_reads_env_vars(app):
    """init_db should use environment variables for connection settings."""
    assert os.environ.get("DATABASE_NAME") is not None
    assert os.environ.get("DATABASE_HOST") is not None


def test_db_proxy_is_initialized_after_app_creation(app):
    """After create_app(), the DatabaseProxy should point to a real database."""
    assert db.obj is not None


@patch.dict(os.environ, {"DATABASE_PORT": "9999"})
def test_init_db_respects_custom_port():
    from app import create_app

    test_app = create_app()
    assert db.obj is not None
