from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app.schemas.application import (
    ApplicationCreateSchema,
    ApplicationUpdateSchema,
    StatusTransitionSchema,
    ApplicationResponseSchema,
)
from app.services import application_service

applications_bp = Blueprint("applications", __name__)

create_schema = ApplicationCreateSchema()
update_schema = ApplicationUpdateSchema()
transition_schema = StatusTransitionSchema()
response_schema = ApplicationResponseSchema()
response_many_schema = ApplicationResponseSchema(many=True)


@applications_bp.route("", methods=["GET"])
@jwt_required()
def list_applications():
    user_id = int(get_jwt_identity())
    status_filter = request.args.get("status")
    try:
        apps = application_service.get_applications(user_id, status_filter)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(response_many_schema.dump(apps)), 200


@applications_bp.route("", methods=["POST"])
@jwt_required()
def create_application():
    user_id = int(get_jwt_identity())
    try:
        data = create_schema.load(request.get_json())
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "messages": e.messages}), 422

    app = application_service.create_application(user_id, data)
    return jsonify(response_schema.dump(app)), 201


@applications_bp.route("/<int:application_id>", methods=["GET"])
@jwt_required()
def get_application(application_id):
    user_id = int(get_jwt_identity())
    try:
        app = application_service.get_application(user_id, application_id)
    except LookupError as e:
        return jsonify({"error": str(e)}), 404
    return jsonify(response_schema.dump(app)), 200


@applications_bp.route("/<int:application_id>", methods=["PATCH"])
@jwt_required()
def update_application(application_id):
    user_id = int(get_jwt_identity())
    try:
        data = update_schema.load(request.get_json())
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "messages": e.messages}), 422

    try:
        app = application_service.update_application(user_id, application_id, data)
    except LookupError as e:
        return jsonify({"error": str(e)}), 404
    return jsonify(response_schema.dump(app)), 200


@applications_bp.route("/<int:application_id>/status", methods=["PATCH"])
@jwt_required()
def transition_status(application_id):
    user_id = int(get_jwt_identity())
    try:
        data = transition_schema.load(request.get_json())
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "messages": e.messages}), 422

    try:
        app = application_service.transition_status(user_id, application_id, data["status"])
    except LookupError as e:
        return jsonify({"error": str(e)}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 422
    return jsonify(response_schema.dump(app)), 200


@applications_bp.route("/<int:application_id>", methods=["DELETE"])
@jwt_required()
def delete_application(application_id):
    user_id = int(get_jwt_identity())
    try:
        application_service.delete_application(user_id, application_id)
    except LookupError as e:
        return jsonify({"error": str(e)}), 404
    return jsonify({"message": "Deleted"}), 200


@applications_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_stats():
    user_id = int(get_jwt_identity())
    return jsonify(application_service.get_stats(user_id)), 200