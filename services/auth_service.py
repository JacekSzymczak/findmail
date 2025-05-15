from datetime import UTC, datetime

from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db
from models import User
from services.invitation_key_service import InvitationKeyService


class AuthService:
    @staticmethod
    def register(email, password, invitation_key):
        """Register a new user."""
        # Validate invitation key
        invitation = InvitationKeyService.validate_invitation_key(invitation_key)

        # Create user
        user = User(
            email=email,
            password=generate_password_hash(password),
        )
        db.session.add(user)

        # Mark invitation key as used
        invitation.used_at = datetime.now(UTC)

        db.session.commit()

        return user

    @staticmethod
    def login(email, password):
        """Login a user."""
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            raise ValueError("Nieprawidłowy email lub hasło")

        login_user(user)
        return user

    @staticmethod
    def logout():
        """Logout the current user."""
        logout_user()

    @staticmethod
    def get_user_by_id(user_id):
        """Load user instance by ID for Flask-Login."""
        return User.query.get(user_id)
