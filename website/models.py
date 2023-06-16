from flask_login import UserMixin
from sqlalchemy.sql import func
from . import db, FLASK_SECRET
from time import time
import jwt


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    g_id = db.Column(db.String(150), unique=True)
    picture_url = db.Column(db.String(2048))

    def get_reset_token(self, expires=500):
        return jwt.encode({"reset_password": self.id, "exp": time() + expires}, key=FLASK_SECRET)
