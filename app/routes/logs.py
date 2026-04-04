from flask import Blueprint, jsonify

logs_bp = Blueprint("logs", __name__)

log_records = []


@logs_bp.route("/logs", methods=["GET"])
def get_logs():
    return jsonify({"logs": log_records[-50:]})