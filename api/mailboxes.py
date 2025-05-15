from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from schemas.mailbox_schema import MailboxSchema
from services.mailbox_service import MailboxService

mailboxes_bp = Blueprint("mailboxes", __name__, url_prefix="/api/mailboxes")


@mailboxes_bp.route("", methods=["POST"])
@login_required
def create_or_access_mailbox():
    """Create or access a mailbox by name."""
    # CSRF protection
    csrf_token = request.headers.get("X-CSRF-Token")
    if not csrf_token:
        return jsonify(error={"code": "401", "message": "Missing CSRF token"}), 401

    if not request.is_json:
        return jsonify(error={"code": "415", "message": "Unsupported Media Type"}), 415

    try:
        data = MailboxSchema().load(request.get_json())
    except ValidationError as err:
        return jsonify(error={"code": "400", "message": err.messages}), 400

    try:
        mailbox = MailboxService.get_or_create(data["name"], current_user)
    except IntegrityError:
        return jsonify(error={"code": "409", "message": "Mailbox name conflict"}), 409
    except Exception as e:
        current_app.logger.error(f"Error creating/accessing mailbox: {e}")
        return jsonify(error={"code": "500", "message": "Internal Server Error"}), 500

    return jsonify(data={"id": mailbox.id, "name": mailbox.name}, meta={}), 201


@mailboxes_bp.route("/generate-random", methods=["POST"])
@login_required
def generate_random_mailbox():
    """Generate a random mailbox name and persist it."""
    # CSRF protection
    csrf_token = request.headers.get("X-CSRF-Token")
    if not csrf_token:
        return jsonify(error={"code": "401", "message": "Missing CSRF token"}), 401

    try:
        mailbox = MailboxService.generate_random(current_user)
    except IntegrityError:
        return jsonify(error={"code": "409", "message": "Mailbox name conflict"}), 409
    except Exception as e:
        current_app.logger.error(f"Error generating random mailbox: {e}")
        return jsonify(error={"code": "500", "message": "Internal Server Error"}), 500

    return jsonify(data={"id": mailbox.id, "name": mailbox.name}, meta={}), 201


@mailboxes_bp.route("/<string:name>", methods=["GET"])
@login_required
def get_mailbox(name):
    """Retrieve mailbox metadata."""
    # Validate mailbox name
    try:
        MailboxSchema().load({"name": name})
    except ValidationError as err:
        return jsonify(error={"code": "400", "message": err.messages}), 400
    try:
        mailbox = MailboxService.get_or_create(name, current_user)
    except Exception as e:
        current_app.logger.error(f"Error retrieving mailbox: {e}")
        return jsonify(error={"code": "500", "message": "Internal Server Error"}), 500

    return jsonify(data={"id": mailbox.id, "name": mailbox.name}, meta={}), 200
