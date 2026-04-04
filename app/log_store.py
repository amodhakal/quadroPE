"""Shared in-memory log record buffer.

This module holds the global list used by ListHandler (in app/__init__.py)
and the /logs endpoint (in app/routes/logs.py) so that neither layer has to
import from the other.

Note: Each gunicorn worker maintains its own copy of this list.  GET /logs
will therefore only return records captured by the worker that handles that
particular request.
"""

log_records: list = []
