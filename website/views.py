from flask import Blueprint, render_template
from flask_login import current_user

views = Blueprint("views", __name__)


@views.route("/", methods=["GET", "POST"])
def home():
    return render_template("home.html", user=current_user)


@views.route("/privacy", methods=["GET", "POST"])
def privacy():
    return render_template("privacy.html", user=current_user)


@views.route("/terms", methods=["GET", "POST"])
def terms():
    return render_template("terms.html", user=current_user)
