import json
import logging
import sys
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from app.database import init_db
from app.routes import register_routes
from app.routes.logs import log_records


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        try:
            log_data["method"] = request.method
            log_data["path"] = request.path
            log_data["remote_addr"] = request.headers.get(
                "X-Forwarded-For", request.remote_addr
            )
        except RuntimeError:
            pass

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class ListHandler(logging.Handler):
    def emit(self, record):
        try:
            log_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }

            try:
                log_data["method"] = request.method
                log_data["path"] = request.path
                log_data["remote_addr"] = request.headers.get(
                    "X-Forwarded-For", request.remote_addr
                )
            except RuntimeError:
                pass

            log_records.append(log_data)

            if len(log_records) > 200:
                del log_records[:-200]
        except Exception:
            pass


def configure_logging(app):
    json_handler = logging.StreamHandler()
    json_handler.setFormatter(JsonFormatter())

    list_handler = ListHandler()

    app.logger.handlers.clear()
    app.logger.addHandler(json_handler)
    app.logger.addHandler(list_handler)
    app.logger.setLevel(logging.DEBUG)
    app.logger.propagate = False

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(json_handler)
    root_logger.addHandler(list_handler)
    root_logger.setLevel(logging.DEBUG)

    werkzeug_logger = logging.getLogger("werkzeug")
    werkzeug_logger.handlers.clear()
    werkzeug_logger.addHandler(json_handler)
    werkzeug_logger.addHandler(list_handler)
    werkzeug_logger.setLevel(logging.DEBUG)
    werkzeug_logger.propagate = False

    peewee_logger = logging.getLogger("peewee")
    peewee_logger.handlers.clear()
    peewee_logger.addHandler(json_handler)
    peewee_logger.addHandler(list_handler)
    peewee_logger.setLevel(logging.DEBUG)
    peewee_logger.propagate = False


def create_app():
    load_dotenv()

    app = Flask(__name__)

    configure_logging(app)
    init_db(app)

    from app import models  # noqa: F401

    register_routes(app)

    @app.before_request
    def log_request():
        app.logger.info("Request received")

    @app.route("/health")
    def health():
        app.logger.info("Health check requested")
        return jsonify(status="ok")

    @app.errorhandler(400)
    def bad_request(error):
        app.logger.warning(f"Bad request: {error.description}")
        return jsonify({"error": str(error.description)}), 400

    @app.errorhandler(404)
    def not_found(error):
        app.logger.warning("Route not found")
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(422)
    def unprocessable_entity(error):
        app.logger.warning("Unprocessable entity")
        return jsonify({"error": "Unprocessable entity"}), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.exception("Internal server error")
        _, exc, _ = sys.exc_info()
        return jsonify({"error": str(exc)}), 500

    return app