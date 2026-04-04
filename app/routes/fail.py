import os
import signal

from flask import Blueprint

fail_bp = Blueprint("fail", __name__)


@fail_bp.route("/fail", methods=["GET"])
def fail():
    os._exit(1) 
    