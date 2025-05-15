from flask import Blueprint, render_template
from flask_login import login_required

main_bp = Blueprint("main_bp", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/mailbox")
@login_required
def mailbox():
    return render_template("mailbox.html")


@main_bp.route("/mailbox/<name>/messages")
@login_required
def messages(name):
    return render_template("messages.html", mailbox={"name": name})
