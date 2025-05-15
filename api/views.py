from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user, login_required, logout_user

views_bp = Blueprint("views_bp", __name__)


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
