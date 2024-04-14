from . import mail, FLASK_SECRET, RECAPTCHA_SECRET_KEY
from flask import current_app, flash
from threading import Thread
from .models import User
import traceback
import requests
import jwt


def _send_mail(msg, app):
    with app.app_context():
        mail.send(msg)


def send_mail(msg):
    Thread(target=_send_mail, args=(msg, current_app._get_current_object())).start()


def verify_reset_token(token) -> User:
    id = jwt.decode(token, key=FLASK_SECRET, algorithms=["HS256"])["reset_password"]
    return User.query.filter_by(id=id).first()


def verify_captcha_token(token) -> bool:
    if token:
        try:
            res = requests.post(
                "https://www.google.com/recaptcha/api/siteverify",
                params={"secret": RECAPTCHA_SECRET_KEY, "response": token},
            )
            res.raise_for_status()
            if not res.json()["success"]:
                print(f'Error verifying captcha: {res.json()["error-codes"]}')
            else:
                print(f"Recaptcha token verification success!\n{res.text}")
            return res.json()["success"]
        except Exception as e:
            print(f"Captcha request failed with: {e}\n {traceback.format_exc()}")
            flash("We can't verify your captcha at the moment... Try again later", category="error")
    return False
