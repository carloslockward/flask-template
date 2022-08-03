from flask import Blueprint
from markdown import markdown


auth = Blueprint("auth", __name__)


@auth.route("/login")
def login():
    return markdown("# Login")


@auth.route("/logout")
def logout():
    return markdown("# Logout")


@auth.route("/sign-up")
def sign_up():
    return markdown("# Sign up")
