import json

from flask import Blueprint, jsonify
from playhouse.shortcuts import model_to_dict

from app.models.event import Event


events_bp = Blueprint("events", __name__)


@events_bp.route("/events", methods=["GET"])
def list_events():
    events = Event.select()
    result = []

    for event in events:
        data = model_to_dict(event, recurse=True)

        user_obj = data.pop("user", None)
        if isinstance(user_obj, dict):
            data["user_id"] = user_obj
        else:
            data["user_id"] = {"id": user_obj}

        url_obj = data.pop("url", None)
        if isinstance(url_obj, dict):
            data["url_id"] = url_obj.get("id")
        else:
            data["url_id"] = url_obj

        try:
            data["details"] = json.loads(data["details"]) if data.get("details") else {}
        except (json.JSONDecodeError, TypeError):
            data["details"] = {}

        result.append(data)

    return jsonify(result)