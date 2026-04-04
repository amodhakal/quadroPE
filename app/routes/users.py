import csv
import os

from flask import Blueprint, abort, current_app, jsonify, request
from peewee import chunked
from playhouse.shortcuts import model_to_dict

from app.database import db
from app.models.user import User

users_bp = Blueprint("users", __name__)

DATA_DIR = os.path.join("./data")


@users_bp.route("/users/bulk", methods=["POST"])
def bulk_import_users():
    if "file" not in request.files:
        current_app.logger.warning("Missing 'file' field in bulk import request")
        abort(400, description="Missing 'file' field")

    file = request.files["file"]
    if not file.filename or not file.filename.endswith(".csv"):
        current_app.logger.warning("Invalid file type for bulk import")
        abort(400, description="Invalid file type, expected .csv")

    reader = csv.DictReader(file.stream.read().decode("utf-8").splitlines())
    rows = [{k: v for k, v in row.items() if k != "id"} for row in reader]

    db.drop_tables([User], cascade=True)
    db.create_tables([User])

    with db.atomic():
        for batch in chunked(rows, 100):
            User.insert_many(batch).execute()

    return jsonify({"imported": len(rows)}), 200


@users_bp.route("/users", methods=["GET"])
def list_users():
    offset = request.args.get("offset", 0, type=int)
    size = request.args.get("size", 20, type=int)

    users = User.select().limit(size).offset(offset)

    return jsonify([model_to_dict(u) for u in users])


@users_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    try:
        user = User.get_by_id(user_id)
    except User.DoesNotExist:
        abort(404)
    return jsonify(model_to_dict(user))


@users_bp.route("/users", methods=["POST"])
def create_user():
    try:
        data = request.get_json(silent=True)
        if not data:
            current_app.logger.warning("Invalid JSON received for create_user")
            abort(400, description="Invalid JSON")
        user = User.create(**data)
        return jsonify(model_to_dict(user)), 201
    except Exception as e:
        current_app.logger.exception(f"Failed to create user: {e}")
        abort(400, description=str(e))


@users_bp.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    try:
        user = User.get_by_id(user_id)
    except User.DoesNotExist:
        abort(404)

    data = request.get_json(silent=True)
    if not data:
        current_app.logger.warning("Invalid JSON received for update_user")
        abort(400, description="Invalid JSON")

    if "username" in data:
        user.username = data["username"]
    if "email" in data:
        user.email = data["email"]

    user.save()
    return jsonify(model_to_dict(user))


@users_bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        user = User.get_by_id(user_id)
    except User.DoesNotExist:
        abort(404)

    user.delete_instance()
    return jsonify({"message": "User deleted", "id": user_id}), 200
