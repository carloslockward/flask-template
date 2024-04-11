from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, USE_GOOGLE_AUTH, GOOGLE_CLIENT_ID, WEBSITE_URL
from .utils import send_mail, verify_reset_token
from google.auth.transport import requests
from google.oauth2 import id_token
from flask_mail import Message
from .models import User

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    redirect_to = request.args.get("redirect_to", "views.home")
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in successfully!", category="success")
                login_user(user, remember=True)
                return redirect(url_for(redirect_to))
            else:
                flash("Incorrect password, try again.", category="error")
        else:
            flash("Email does not exist.", category="error")

    return render_template(
        "login.html",
        user=current_user,
        google_scripts=USE_GOOGLE_AUTH,
        client_id=GOOGLE_CLIENT_ID,
        redirect_to=redirect_to,
    )


@auth.route("/login_google", methods=["GET", "POST"])
def login_google():
    redirect_to = request.args.get("redirect_to", "views.home")
    if request.method == "POST":
        csrf_token_cookie = request.cookies.get("g_csrf_token")
        if not csrf_token_cookie:
            flash("No CSRF token in Cookie.", category="error")
            return redirect(url_for("auth.login"))
        csrf_token_body = request.form.get("g_csrf_token")
        if not csrf_token_body:
            flash("No CSRF token in post body.", category="error")
            return redirect(url_for("auth.login"))
        if csrf_token_cookie != csrf_token_body:
            flash("Failed to verify double submit cookie.", category="error")
            return redirect(url_for("auth.login"))

        idinfo = id_token.verify_oauth2_token(
            request.form.get("credential"),
            requests.Request(),
            GOOGLE_CLIENT_ID,
        )
        g_id = idinfo["sub"]

        user = User.query.filter_by(g_id=g_id).first()

        if user:
            flash("Logged in successfully!", category="success")
            login_user(user, remember=True)
            return redirect(url_for(redirect_to))
        else:
            email = idinfo["email"]
            first_name = idinfo["given_name"]
            last_name = idinfo["family_name"]
            picture_url = idinfo["picture"]
            new_user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                password="",
                g_id=g_id,
                picture_url=picture_url,
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("Account created!", category="success")
            return redirect(url_for(redirect_to))

    return redirect(url_for(redirect_to))


@auth.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        token = request.args.get("t")
        if token:
            try:
                user = verify_reset_token(token=token)
            except Exception as e:
                if "expired" in str(e):
                    flash("Password reset link has expired! Try again", category="error")
                    return redirect(url_for("auth.login"))
                else:
                    raise e
            if user:
                password1 = request.form.get("password1")
                password2 = request.form.get("password2")
                if password1 != password2:
                    flash("Passwords don't match.", category="error")
                    return render_template("reset_pass.html", user=None)
                elif len(password1) < 7:
                    flash("Password must be at least 7 characters.", category="error")
                    return render_template("reset_pass.html", user=None)
                else:
                    user.password = generate_password_hash(password1, method="sha256")
                    db.session.commit()
                    flash("Password updated! Try logging in", category="success")
                    return redirect(url_for("auth.login"))
            else:
                flash(f"Unknown error... Try again", category="error")
                return redirect(url_for("auth.login"))
        else:
            flash("Invalid request!", category="error")
            return redirect(url_for("auth.login"))
    else:
        token = request.args.get("t")
        if not token:
            flash("Invalid request!", category="error")
            return redirect(url_for("auth.login"))
        return render_template("reset_pass.html", user=None)


@auth.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        # TODO: Make tokens one time only
        email = request.form.get("email")

        user: User = User.query.filter_by(email=email).first()
        if user:
            token = user.get_reset_token()
            msg = Message()
            msg.subject = "App Password Reset"
            msg.recipients = [user.email]
            msg.body = f"""Hello {user.first_name},

We received a password reset request for your account({user.email}) if you did not ask for this, please ignore this email.
Otherwise click the link below to reset your password.

http://{WEBSITE_URL}/reset_password?t={token}
            
            """
            send_mail(msg)
            flash(
                "A password reset email has been sent! If you can't see it, check your spam folder.",
                category="info",
            )
            return redirect(url_for("views.home"))
        else:
            flash(
                "An error ocurred!",
                category="error",
            )

    return render_template("forgot_pass.html", user=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        first_name = request.form.get("firstName", "")
        last_name = request.form.get("lastName", "")
        password1 = request.form.get("password1", "")
        password2 = request.form.get("password2", "")

        if email is None:
            flash("Email must not be empty!.", category="error")
        else:
            user = User.query.filter_by(email=email).first()
            if user:
                flash("Email already exists.", category="error")
            elif len(email) < 4:
                flash("Email must be greater than 3 characters.", category="error")
            elif len(first_name) < 2:
                flash("First name must be greater than 1 character.", category="error")
            elif len(last_name) < 2:
                flash("Last name must be greater than 1 character.", category="error")
            elif password1 != password2:
                flash("Passwords don't match.", category="error")
            elif len(password1) < 7:
                flash("Password must be at least 7 characters.", category="error")
            else:
                new_user = User(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=generate_password_hash(password1, method="sha256"),
                )
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)
                flash("Account created!", category="success")
                return redirect(url_for("views.home"))

    return render_template(
        "sign_up.html",
        user=current_user,
        google_scripts=USE_GOOGLE_AUTH,
        client_id=GOOGLE_CLIENT_ID,
    )
