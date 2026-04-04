import json

from flask import Blueprint, abort, current_app, jsonify, request
from playhouse.shortcuts import model_to_dict

from app.models.event import Event
from app.models.url import Url
from app.models.user import User

events_bp = Blueprint("events", __name__)


def format_event(event):
    d = model_to_dict(event)
    d["url_id"] = {"id": d.pop("url")}
    d["user_id"] = {"id": d.pop("user")}
    try:
        d["details"] = json.loads(d["details"])
    except (json.JSONDecodeError, TypeError):
        d["details"] = {}
    return d


@events_bp.route("/events", methods=["GET"])
def list_events():
    query = Event.select()

    if "url_id" in request.args:
        query = query.where(Event.url == request.args.get("url_id", type=int))
    if "user_id" in request.args:
        query = query.where(Event.user == request.args.get("user_id", type=int))
    if "event_type" in request.args:
        query = query.where(Event.event_type == request.args["event_type"])

    result = [format_event(e) for e in query]
    return jsonify(result)


@events_bp.route("/events", methods=["POST"])
def create_event():
    data = request.get_json(silent=True)
    if not data:
        current_app.logger.warning("Invalid JSON received for create_event")
        abort(400, description="Invalid JSON")

    url_id = data.get("url_id")
    user_id = data.get("user_id")
    event_type = data.get("event_type")
    details = data.get("details", {})

    if not url_id or not isinstance(url_id, int):
        current_app.logger.warning("url_id must be an integer")
        abort(400, description="url_id must be an integer")
    if not user_id or not isinstance(user_id, int):
        current_app.logger.warning("user_id must be an integer")
        abort(400, description="user_id must be an integer")
    if not event_type or not isinstance(event_type, str):
        current_app.logger.warning("event_type must be a string")
        abort(400, description="event_type must be a string")

    try:
        Url.get_by_id(url_id)
    except Url.DoesNotExist:
        current_app.logger.warning("URL not found")
        abort(400, description="URL not found")

    try:
        User.get_by_id(user_id)
    except User.DoesNotExist:
        current_app.logger.warning("User not found")
        abort(400, description="User not found")

    event = Event.create(
        url_id=url_id,
        user_id=user_id,
        event_type=event_type,
        details=json.dumps(details),
    )

    current_app.logger.info(f"Event created: type={event_type} url_id={url_id}")
    return jsonify(format_event(event)), 201
