from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask import Flask
from os import path

db = SQLAlchemy()
mail = Mail()

DB_NAME = "database.db"
FLASK_SECRET = "Your secret key here!"
USE_GOOGLE_AUTH = True
GOOGLE_CLIENT_ID = "Your google client_id here!"
WEBSITE_URL = "localhost:5000"  # TODO: Replace with your domain name when app is live.


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = FLASK_SECRET
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USERNAME"] = "your_email_here@gmail.com"
    app.config["MAIL_PASSWORD"] = "your password here"
    db.init_app(app)
    mail.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from .models import User

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
