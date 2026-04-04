import os

import psutil
from flask import Blueprint, jsonify


metrics_bp = Blueprint("metrics", __name__)


@metrics_bp.route("/metrics", methods=["GET"])
def get_metrics():
    process = psutil.Process(os.getpid())

    memory = psutil.virtual_memory()
    used_gb = round(memory.used / 1024 / 1024 / 1024, 1)
    total_gb = round(memory.total / 1024 / 1024 / 1024, 1)

    cpu_percent = psutil.cpu_percent(interval=1)
    process_memory_mb = round(process.memory_info().rss / 1024 / 1024, 1)

    return jsonify(
        {
            "cpu_percent": cpu_percent,
            "system_ram": {
                "used_gb": used_gb,
                "total_gb": total_gb,
            },
            "process_memory_mb": process_memory_mb,
        }
    )