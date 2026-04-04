import json
import logging
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from app.database import init_db
from app.routes import register_routes


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


def configure_logging(app):
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    app.logger.handlers.clear()
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    app.logger.propagate = False

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

    werkzeug_logger = logging.getLogger("werkzeug")
    werkzeug_logger.handlers.clear()
    werkzeug_logger.addHandler(handler)
    werkzeug_logger.setLevel(logging.INFO)
    werkzeug_logger.propagate = False


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
        return jsonify({"error": "Internal server error"}), 500

    return app
