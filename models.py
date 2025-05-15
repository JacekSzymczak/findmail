from datetime import UTC, datetime
from functools import wraps

from flask import abort
from flask_login import UserMixin
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from extensions import db


class InvitationKey(db.Model):
    __tablename__ = "invitation_keys"
    id = Column(Integer, primary_key=True)
    key = Column(String(64), unique=True, nullable=False)
    used_by = relationship("User", back_populates="invitation_key", uselist=False)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(db.DateTime, default=lambda: datetime.now(UTC))
    is_admin = Column(Boolean, default=False)
    invitation_key_id = Column(Integer, ForeignKey("invitation_keys.id"))
    invitation_key = relationship("InvitationKey", back_populates="used_by")


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_login import current_user

        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403, description="Brak uprawnień administratora")
        return f(*args, **kwargs)

    return decorated_function
