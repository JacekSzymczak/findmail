import secrets

from flask_login import current_user

from extensions import db
from models import InvitationKey


class InvitationKeyService:
    @staticmethod
    def create_invitation_key():
        """Create a new invitation key."""
        if not current_user.is_authenticated or not current_user.is_admin:
            raise ValueError("Brak uprawnień administratora")

        # Generate a shorter key that fits within the 64-character limit
        key = secrets.token_urlsafe(32)[:32]  # This will give us a ~43 character string
        invitation_key = InvitationKey(key=key)
        db.session.add(invitation_key)
        db.session.commit()
        return invitation_key

    @staticmethod
    def list_invitation_keys():
        """List all invitation keys."""
        if not current_user.is_authenticated or not current_user.is_admin:
            raise ValueError("Brak uprawnień administratora")

        return InvitationKey.query.all()

    @staticmethod
    def get_invitation_key(key):
        """Get an invitation key by its value."""
        return InvitationKey.query.filter_by(key=key).first()

    @staticmethod
    def delete_invitation_key(key):
        """Delete an invitation key (admin only)."""
        if not current_user.is_authenticated or not current_user.is_admin:
            raise ValueError("Brak uprawnień administratora")
        return InvitationKeyService._delete_invitation_key_noauth(key)

    @staticmethod
    def _delete_invitation_key_noauth(key):
        """Delete an invitation key without checking admin rights (for registration logic)."""
        invitation_key = InvitationKeyService.get_invitation_key(key)
        if not invitation_key:
            return False
        db.session.delete(invitation_key)
        db.session.commit()
        return True

    @staticmethod
    def validate_invitation_key(key):
        """Validate an invitation key."""
        invitation_key = InvitationKeyService.get_invitation_key(key)
        if not invitation_key:
            raise ValueError("Nieprawidłowy klucz zaproszenia")

        return invitation_key

    @staticmethod
    def delete(key):
        """Delete a specific invitation key (admin only)."""
        return InvitationKeyService.delete_invitation_key(key)
