from flask import Blueprint, jsonify

from app.log_store import log_records

logs_bp = Blueprint("logs", __name__)


@logs_bp.route("/logs", methods=["GET"])
def get_logs():
    return jsonify({"logs": log_records[-50:]})