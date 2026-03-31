from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from marshmallow import ValidationError
from app.schemas.auth import RegisterSchema, LoginSchema, UserResponseSchema
from app.services.auth_service import register_user, authenticate_user

auth_bp = Blueprint("auth", __name__)

register_schema = RegisterSchema()
login_schema = LoginSchema()
user_response_schema = UserResponseSchema()


@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = register_schema.load(request.get_json())
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "messages": e.messages}), 422

    try:
        user = register_user(data["email"], data["password"])
    except ValueError as e:
        return jsonify({"error": str(e)}), 409

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user_response_schema.dump(user)}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = login_schema.load(request.get_json())
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "messages": e.messages}), 422

    try:
        user = authenticate_user(data["email"], data["password"])
    except ValueError as e:
        return jsonify({"error": str(e)}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user_response_schema.dump(user)}), 200