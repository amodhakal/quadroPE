from flask import Blueprint, jsonify
from app.utils.logger import setup_logger
import logging

logs_bp = Blueprint("logs", __name__)

log_records = []

class ListHandler(logging.Handler):
    def emit(self, record):
        log_records.append({
            "timestamp": self.formatter.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        })

handler = ListHandler()
handler.setFormatter(logging.Formatter())
logging.getLogger("quadroPE").addHandler(handler)

@logs_bp.route("/logs", methods=["GET"])
def get_logs():
    return jsonify({"logs": log_records[-50:]})