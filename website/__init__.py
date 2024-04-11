from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask import Flask

db = SQLAlchemy()
mail = Mail()

DB_NAME = "database.db"
FLASK_SECRET = "Your secret key here!" # REPLACE with your google client_id when app is live.
USE_GOOGLE_AUTH = True # CONFIG Turn off if you dont want to use google OAuth
GOOGLE_CLIENT_ID = "Your google client_id here!" # REPLACE with your google client_id when app is live.
WEBSITE_URL = "localhost:5000"  # REPLACE with your domain name when app is in production.


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = FLASK_SECRET
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_DEFAULT_SENDER"] = "no-reply@website.com" # REPLACE
    app.config["MAIL_USERNAME"] = "your_email_here@gmail.com" # REPLACE
    app.config["MAIL_PASSWORD"] = "your password here" # REPLACE
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
