from flask import Blueprint, current_app, jsonify
from flask_login import current_user, login_required
from flask_wtf.csrf import CSRFProtect
from marshmallow import ValidationError

from schemas.mailbox_schema import MailboxSchema
from schemas.message_schema import MessageSchema
from services.mailbox_service import MailboxService
from services.message_service import MessageService

messages_bp = Blueprint("messages", __name__, url_prefix="/api/mailboxes")
csrf = CSRFProtect()


@messages_bp.route("/<string:name>/messages", methods=["GET"])
@login_required
def list_messages(name):
    """List messages in a mailbox."""
    # Validate mailbox name
    try:
        MailboxSchema().load({"name": name})
    except ValidationError as err:
        return jsonify(error={"code": "400", "message": err.messages}), 400

    try:
        mailbox = MailboxService.get_or_create(name, current_user)
        messages = MessageService.list_messages(mailbox["name"])
    except Exception as e:
        current_app.logger.error(f"Error listing messages: {e}")
        return jsonify(error={"code": "500", "message": "Internal Server Error"}), 500

    return jsonify(
        data={"messages": [MessageSchema().dump(m) for m in messages]},
        meta={"total": len(messages)},
    ), 200


@messages_bp.route("/<string:name>/messages/<string:message_id>", methods=["GET"])
@login_required
def get_message(name, message_id):
    """Retrieve a single message content."""
    try:
        MailboxSchema().load({"name": name})
    except ValidationError as err:
        return jsonify(error={"code": "400", "message": err.messages}), 400

    try:
        mailbox = MailboxService.get_or_create(name, current_user)
        message = MessageService.get_message(mailbox["name"], message_id)
        if not message:
            return jsonify(error={"code": "404", "message": "Message not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Error retrieving message: {e}")
        return jsonify(error={"code": "500", "message": "Internal Server Error"}), 500

    return jsonify(data={"message": MessageSchema().dump(message)}), 200


@messages_bp.route("/<string:name>/messages/<string:message_id>", methods=["DELETE"])
@login_required
def delete_message(name, message_id):
    """Permanently delete a message."""
    try:
        # Validate mailbox name
        MailboxSchema().load({"name": name})
    except ValidationError as err:
        return jsonify(error={"code": "400", "message": err.messages}), 400

    try:
        # Delete the message
        mailbox = MailboxService.get_or_create(name, current_user)
        deleted = MessageService.delete_message(mailbox["name"], message_id)

        if not deleted:
            return jsonify(error={"code": "404", "message": "Message not found"}), 404

        return "", 204

    except Exception as e:
        current_app.logger.error(f"Error deleting message: {e}", exc_info=True)
        return jsonify(error={"code": "500", "message": "Internal Server Error"}), 500
