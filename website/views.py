from flask import Blueprint
from markdown import markdown

views = Blueprint("views", __name__)


@views.route("/")
def home():
    return markdown(
        """# This is a template!

This template was created by `carloslockward`."""
    )