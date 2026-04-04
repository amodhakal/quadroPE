import csv
import os

from flask import Blueprint, request, jsonify, abort
from peewee import chunked
from playhouse.shortcuts import model_to_dict

from app.database import db
from app.models.user import User

users_bp = Blueprint("users", __name__)

DATA_DIR = os.path.join("./data")

@users_bp.route("/users/bulk", methods=["POST"])
def bulk_import_users():
    data = request.get_json(silent=True)
    if not data:
        print("400: Missing JSON body")
        abort(400, description="Missing JSON body")

    if "file" not in data:
        print("400: Missing 'file' field")
        abort(400, description="Missing 'file' field")

    if "row_count" not in data:
        print("400: Missing 'row_count' field")
        abort(400, description="Missing 'row_count' field")

    file_path = os.path.join(DATA_DIR, data["file"])
    row_count = data.get("row_count")

    if not os.path.exists(file_path):
        print(f"400: File not found: {file_path}")
        abort(400, description=f"File not found: {data['file']}")

    with open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)[:row_count]

    db.drop_tables([User], cascade=True)
    db.create_tables([User])

    with db.atomic():
        for batch in chunked(rows, 100):
            User.insert_many(batch).execute()

    return "OK"


@users_bp.route("/users", methods=["GET"])
def list_users():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    total = User.select().count()
    offset = (page - 1) * per_page
    users = User.select().limit(per_page).offset(offset)

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
            print("400: Invalid JSON")
            abort(400, description="Invalid JSON")
        user = User.create(**data)
        return jsonify(model_to_dict(user)), 201
    except Exception as e:
        print(f"400: {e}")
        abort(400, description=str(e))


@users_bp.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    try:
        user = User.get_by_id(user_id)
    except User.DoesNotExist:
        abort(404)

    data = request.get_json(silent=True)
    if not data:
        print("400: Invalid JSON")
        abort(400, description="Invalid JSON")

    if "username" in data:
        user.username = data["username"]
    if "email" in data:
        user.email = data["email"]

    user.save()
    return jsonify(model_to_dict(user))
