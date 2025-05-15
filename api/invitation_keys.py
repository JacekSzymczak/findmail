from flask import Blueprint, current_app, jsonify, request
from flask_login import login_required
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from extensions import csrf
from models import admin_required
from schemas.invitation_key_schema import InvitationKeySchema
from services.invitation_key_service import InvitationKeyService

invitation_keys_bp = Blueprint(
    "invitation_keys", __name__, url_prefix="/api/invitation-keys"
)


@invitation_keys_bp.route("", methods=["POST"])
@login_required
@admin_required
@csrf.exempt
def create_invitation_key():
    """Create a new invitation key."""
    if not request.is_json:
        return jsonify(error={"code": "415", "message": "Unsupported Media Type"}), 415

    try:
        # Log the incoming JSON data for debugging
        current_app.logger.debug(f"Received invitation key data: {request.get_json()}")
        data = InvitationKeySchema().load(request.get_json())
    except ValidationError as err:
        return jsonify(error={"code": "400", "message": err.messages}), 400

    try:
        key = InvitationKeyService.create(data["key"])
    except IntegrityError:
        return jsonify(
            error={"code": "409", "message": "Klucz zaproszenia już istnieje"}
        ), 409
    except Exception as e:
        current_app.logger.error(f"Błąd podczas tworzenia klucza zaproszenia: {e}")
        return jsonify(error={"code": "500", "message": "Wewnętrzny błąd serwera"}), 500

    return jsonify(data={"key": key}, meta={}), 201


@invitation_keys_bp.route("", methods=["GET"])
@login_required
@admin_required
def list_invitation_keys():
    """List all unused invitation keys."""
    try:
        keys = InvitationKeyService.list_unused()
    except Exception as e:
        current_app.logger.error(f"Błąd podczas listowania kluczy zaproszeń: {e}")
        return jsonify(error={"code": "500", "message": "Wewnętrzny błąd serwera"}), 500
    return jsonify(data={"keys": keys}, meta={}), 200


@invitation_keys_bp.route("/<string:key>", methods=["DELETE"])
@login_required
@admin_required
@csrf.exempt
def delete_invitation_key(key):
    """Delete a specific invitation key."""
    try:
        deleted = InvitationKeyService.delete(key)
        if not deleted:
            return jsonify(
                error={"code": "404", "message": "Nie znaleziono klucza zaproszenia"}
            ), 404
    except Exception as e:
        current_app.logger.error(f"Błąd podczas usuwania klucza zaproszenia: {e}")
        return jsonify(error={"code": "500", "message": "Wewnętrzny błąd serwera"}), 500
    return "", 204
