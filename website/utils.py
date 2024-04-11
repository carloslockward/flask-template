from . import mail, FLASK_SECRET
from flask import current_app
from threading import Thread
from .models import User
import jwt


def _send_mail(msg, app):
    with app.app_context():
        mail.send(msg)


def send_mail(msg):
    Thread(target=_send_mail, args=(msg, current_app._get_current_object())).start()


def verify_reset_token(token) -> User:
    id = jwt.decode(token, key=FLASK_SECRET, algorithms=["HS256"])["reset_password"]
    return User.query.filter_by(id=id).first()
