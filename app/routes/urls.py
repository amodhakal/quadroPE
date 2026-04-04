import random
import string

from flask import Blueprint, abort, current_app, jsonify, request
from playhouse.shortcuts import model_to_dict

from app.models.url import Url
from app.models.user import User
from app.utils.events import create_event

urls_bp = Blueprint("urls", __name__)


def generate_short_code(length=6):
    while True:
        code = "".join(random.choices(string.ascii_letters + string.digits, k=length))
        if not Url.select().where(Url.short_code == code).exists():
            return code


def format_url(url):
    data = model_to_dict(url)
    data["user_id"] = data.pop("user")
    return data


@urls_bp.route("/urls", methods=["POST"])
def create_url():
    data = request.get_json(silent=True)

    if not data:
        current_app.logger.warning("Invalid JSON received for create_url")
        abort(400, description="Invalid JSON")

    user_id = data.get("user_id")
    original_url = data.get("original_url")
    title = data.get("title")

    if not user_id or not isinstance(user_id, int):
        current_app.logger.warning("user_id must be an integer")
        abort(400, description="user_id must be an integer")

    if not original_url or not isinstance(original_url, str):
        current_app.logger.warning("original_url must be a string")
        abort(400, description="original_url must be a string")

    if not title or not isinstance(title, str):
        current_app.logger.warning("title must be a string")
        abort(400, description="title must be a string")

    try:
        User.get_by_id(user_id)
    except User.DoesNotExist:
        current_app.logger.warning("User not found")
        abort(400, description="User not found")

    short_code = generate_short_code()

    url = Url.create(
        user_id=user_id,
        short_code=short_code,
        original_url=original_url,
        title=title,
        is_active=True,
    )

    create_event(
        url.id,
        user_id,
        "created",
        {
            "short_code": short_code,
            "original_url": original_url,
        },
    )

    current_app.logger.info(
        f"Short URL created with id={url.id} short_code={short_code}"
    )

    return jsonify(format_url(url)), 201


@urls_bp.route("/urls", methods=["GET"])
def list_urls():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)

    query = Url.select()

    if "id" in request.args:
        query = query.where(Url.id == request.args.get("id", type=int))

    if "user_id" in request.args:
        query = query.where(Url.user_id == request.args.get("user_id", type=int))

    if "short_code" in request.args:
        query = query.where(Url.short_code == request.args["short_code"])

    if "original_url" in request.args:
        query = query.where(Url.original_url == request.args["original_url"])

    if "is_active" in request.args:
        val = request.args["is_active"].lower()
        query = query.where(Url.is_active == (val == "true"))

    offset = (page - 1) * per_page
    urls = list(query.limit(per_page).offset(offset))
    current_app.logger.info(f"Listed {len(urls)} URL records")

    return jsonify({"kind": "list", "items": [format_url(u) for u in urls]})


@urls_bp.route("/urls/<int:url_id>", methods=["GET"])
def get_url(url_id):
    try:
        url = Url.get_by_id(url_id)
    except Url.DoesNotExist:
        current_app.logger.warning(f"URL not found for id={url_id}")
        abort(404)
    except Exception as e:
        current_app.logger.exception(f"Unexpected error fetching URL id={url_id}: {e}")
        abort(500, description="Internal server error")

    current_app.logger.info(f"Fetched URL id={url_id}")
    return jsonify(format_url(url))


@urls_bp.route("/urls/<int:url_id>", methods=["PUT"])
def update_url(url_id):
    try:
        url = Url.get_by_id(url_id)
    except Url.DoesNotExist:
        current_app.logger.warning(f"URL not found for update id={url_id}")
        abort(404)

    data = request.get_json(silent=True)

    if not data:
        current_app.logger.warning("Invalid JSON received for update_url")
        abort(400, description="Invalid JSON")

    if "title" in data:
        url.title = data["title"]
        create_event(
            url.id,
            url.user_id,
            "updated",
            {
                "field": "title",
                "new_value": data["title"],
            },
        )
        current_app.logger.info(f"Updated title for url id={url.id}")

    if "is_active" in data:
        url.is_active = data["is_active"]
        create_event(
            url.id,
            url.user_id,
            "updated",
            {
                "field": "is_active",
                "new_value": data["is_active"],
            },
        )
        current_app.logger.info(f"Updated is_active for url id={url.id}")

    url.save()
    return jsonify(format_url(url))


@urls_bp.route("/urls/<int:url_id>", methods=["DELETE"])
def delete_url(url_id):
    try:
        url = Url.get_by_id(url_id)
    except Url.DoesNotExist:
        current_app.logger.warning(f"URL not found for delete id={url_id}")
        abort(404)

    url.delete_instance()
    current_app.logger.info(f"Deleted URL id={url_id}")
    return jsonify({"message": "URL deleted", "id": url_id}), 200


@urls_bp.route("/r/<short_code>", methods=["GET"])
def redirect_short_code(short_code):
    try:
        url = Url.select().where(Url.short_code == short_code).get()
    except Url.DoesNotExist:
        current_app.logger.warning(f"Short code not found: {short_code}")
        abort(404)

    if not url.is_active:
        current_app.logger.warning(f"Short code inactive: {short_code}")
        abort(404)

    create_event(
        url.id,
        url.user_id,
        "click",
        {"short_code": short_code},
    )

    current_app.logger.info(
        f"Redirecting short code {short_code} to {url.original_url}"
    )
    return jsonify({"url": url.original_url, "short_code": short_code})
