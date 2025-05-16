from functools import wraps

from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user, login_required, logout_user

views_bp = Blueprint("views_bp", __name__)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect(url_for("views_bp.login"))
        return f(*args, **kwargs)

    return decorated_function


@views_bp.route("/login", methods=["GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("views_bp.mailbox"))
    return render_template("auth.html", active_tab="login")


@views_bp.route("/register", methods=["GET"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("views_bp.mailbox"))
    return render_template("auth.html", active_tab="register")


@views_bp.route("/logout", methods=["GET"])
def logout():
    logout_user()
    return redirect(url_for("views_bp.login"))


@views_bp.route("/mailbox", methods=["GET"])
@login_required
def mailbox():
    return render_template("mailbox.html")


@views_bp.route("/admin", methods=["GET"])
@login_required
@admin_required
def admin():
    from models import InvitationKey

    invite_keys = InvitationKey.query.order_by(InvitationKey.id.desc()).all()
    return render_template("admin.html", invite_keys=invite_keys)
