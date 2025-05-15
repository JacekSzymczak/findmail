from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required
from marshmallow import ValidationError

from extensions import csrf
from schemas.mailbox_schema import MailboxSchema
from services.mailbox_service import MailboxService

mailboxes_bp = Blueprint("mailboxes", __name__, url_prefix="/api/mailboxes")


@mailboxes_bp.route("", methods=["POST"])
@login_required
@csrf.exempt
def create_mailbox():
    """Create a new mailbox."""
    if not request.is_json:
        return jsonify(error={"code": "415", "message": "Unsupported Media Type"}), 415
    try:
        data = MailboxSchema().load(request.get_json())
    except ValidationError as err:
        return jsonify(error={"code": "400", "message": err.messages}), 400
    try:
        mailbox = MailboxService.get_or_create(data["name"], current_user)
    except Exception as e:
        current_app.logger.error(f"Błąd podczas tworzenia skrzynki: {e}")
        return jsonify(error={"code": "500", "message": "Wewnętrzny błąd serwera"}), 500
    return jsonify(data={"name": mailbox["name"]}), 201


@mailboxes_bp.route("/generate-random", methods=["POST"])
@login_required
@csrf.exempt
def generate_random_mailbox():
    """Generate a random mailbox name and create it."""
    try:
        mailbox = MailboxService.generate_random(current_user)
    except Exception as e:
        current_app.logger.error(f"Błąd podczas generowania skrzynki: {e}")
        return jsonify(error={"code": "500", "message": "Wewnętrzny błąd serwera"}), 500
    return jsonify(data={"name": mailbox["name"]}), 201


@mailboxes_bp.route("/<string:name>", methods=["GET"])
@login_required
def get_mailbox(name):
    """Get mailbox details."""
    try:
        mailbox = MailboxService.get_or_create(name, current_user)
        if not mailbox:
            return jsonify(
                error={"code": "404", "message": "Nie znaleziono skrzynki"}
            ), 404
    except Exception as e:
        current_app.logger.error(f"Błąd podczas pobierania skrzynki: {e}")
        return jsonify(error={"code": "500", "message": "Wewnętrzny błąd serwera"}), 500
    return jsonify(data={"name": mailbox["name"]}), 200
