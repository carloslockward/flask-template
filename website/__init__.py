from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask import Flask
from os import path

db = SQLAlchemy()
DB_NAME = "database.db"
USE_GOOGLE_AUTH = True
GOOGLE_CLIENT_ID = "Your google client_id here!"


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "Your secret key here!"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    db.init_app(app)

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
