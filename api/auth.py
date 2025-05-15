from flask import Blueprint, current_app, jsonify, request
from flask_login import login_required
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from extensions import csrf, limiter
from schemas.auth_schema import LoginSchema, RegisterSchema
from services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
@limiter.limit("5 per minute")
@csrf.exempt
def register():
    """Register a new user using an invitation key."""
    if not request.is_json:
        return jsonify(error={"code": "415", "message": "Unsupported Media Type"}), 415
    try:
        data = RegisterSchema().load(request.get_json())
    except ValidationError as err:
        return jsonify(error={"code": "400", "message": err.messages}), 400
    try:
        # Check if this is the first user
        from models import User

        is_first_user = User.query.count() == 0

        user = AuthService.register(
            data["email"], data["password"], data["invitation_key"]
        )

        # Make first user an admin
        if is_first_user:
            user.is_admin = True
            current_app.db.session.commit()
            current_app.logger.info(
                f"Pierwszy użytkownik {user.email} został administratorem"
            )

    except IntegrityError:
        return jsonify(error={"code": "409", "message": "Email already exists"}), 409
    except ValueError as e:
        # e.g., invalid invitation key
        return jsonify(error={"code": "401", "message": str(e)}), 401
    except Exception as e:
        current_app.logger.error(f"Error during registration: {e}")
        return jsonify(error={"code": "500", "message": "Internal Server Error"}), 500
    # Assume user has id and email attributes
    return jsonify(data={"id": user.id, "email": user.email}, meta={}), 201


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
@csrf.exempt
def login():
    """Authenticate user and create session."""
    if not request.is_json:
        return jsonify(error={"code": "415", "message": "Unsupported Media Type"}), 415
    try:
        data = LoginSchema().load(request.get_json())
    except ValidationError as err:
        return jsonify(error={"code": "400", "message": err.messages}), 400
    try:
        user = AuthService.login(data["email"], data["password"])
    except ValueError as e:
        return jsonify(error={"code": "401", "message": str(e)}), 401
    except Exception as e:
        current_app.logger.error(f"Error during login: {e}")
        return jsonify(error={"code": "500", "message": "Internal Server Error"}), 500
    return jsonify(data={"id": user.id, "email": user.email}, meta={}), 200


@auth_bp.route("/logout", methods=["POST"])
@login_required
@csrf.exempt
def logout():
    """Invalidate user session."""
    csrf_token = request.headers.get("X-CSRF-Token")
    if not csrf_token:
        return jsonify(error={"code": "401", "message": "Missing CSRF token"}), 401
    try:
        AuthService.logout()
    except Exception as e:
        current_app.logger.error(f"Error during logout: {e}")
        return jsonify(error={"code": "500", "message": "Internal Server Error"}), 500
    return "", 204
