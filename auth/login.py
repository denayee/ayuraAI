from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
from database import get_db
import secrets
from datetime import datetime, timedelta
from routes.email_handler import send_password_reset_email
from request_helpers import get_request_data, wants_json_response

login_bp = Blueprint("login", __name__)

load_dotenv()


@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("recommendation.recommendation"))

    if request.method == "POST":
        is_api_request = wants_json_response()
        data = get_request_data()
        email = data.get("email", "").strip()
        password = data.get("password", "")

        db = get_db()
        try:
            cur = db.cursor()
            cur.execute(
                "SELECT id, name, password, gender, is_admin, age FROM users WHERE email=? OR username=?",
                (email, email),
            )
            user = cur.fetchone()

            if user and check_password_hash(user[2], password):
                session["user_id"] = user[0]
                session["name"] = user[1]
                session["gender"] = user[3] if user[3] else "Not specified"
                session["is_admin"] = bool(user[4])
                session["age"] = user[5] if user[5] else 25

                cur.execute(
                    "SELECT COUNT(*) FROM skin_profile WHERE user_id = ?", (user[0],)
                )
                skin_exists = cur.fetchone()[0] > 0
                cur.execute(
                    "SELECT COUNT(*) FROM hair_profile WHERE user_id = ?", (user[0],)
                )
                hair_exists = cur.fetchone()[0] > 0
                session["profile_complete"] = skin_exists and hair_exists

                redirect_url = (
                    url_for("admin.dashboard")
                    if session["is_admin"]
                    else url_for("recommendation.recommendation")
                )

                if is_api_request:
                    return {
                        "success": True,
                        "message": (
                            "Welcome to AyuraAI Control Center!"
                            if session["is_admin"]
                            else "Welcome back! Let's glow!"
                        ),
                        "redirect": redirect_url,
                        "is_admin": session["is_admin"],
                    }

                flash(
                    "Welcome to AyuraAI Control Center!"
                    if session["is_admin"]
                    else "Welcome back! Let's glow!",
                    "success",
                )
                return redirect(redirect_url)

            if is_api_request:
                return {"success": False, "error": "Invalid email or password"}, 401

            flash("Invalid email or password", "error")
            return redirect(url_for("login.login"))
        except Exception as e:
            if is_api_request:
                return {"success": False, "error": f"An error occurred: {str(e)}"}, 500
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for("login.login"))
        finally:
            db.close()

    return render_template("login.html")


@login_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


@login_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        is_api_request = wants_json_response()
        data = get_request_data()
        email = data.get("email", "").strip()

        db = get_db()
        try:
            cur = db.cursor()
            cur.execute("SELECT id FROM users WHERE email=?", (email,))
            user = cur.fetchone()

            if user:
                token = secrets.token_urlsafe(32)
                expiry = datetime.now() + timedelta(hours=1)
                cur.execute(
                    "UPDATE users SET reset_token=?, reset_token_expiry=? WHERE id=?",
                    (token, expiry, user[0]),
                )
                db.commit()

                reset_url = url_for("login.reset_password", token=token, _external=True)
                if send_password_reset_email(email, reset_url):
                    message = "Reset link sent! Please check your email."
                    if is_api_request:
                        return {"success": True, "message": message}
                    flash(message, "success")
                else:
                    error_message = (
                        "Failed to send email. There might be a configuration issue."
                    )
                    if is_api_request:
                        return {"success": False, "error": error_message}, 500
                    flash(error_message, "error")
            else:
                info_message = (
                    "If that email exists in our system, you will receive a reset link."
                )
                if is_api_request:
                    return {"success": True, "message": info_message}
                flash(info_message, "info")

            return redirect(url_for("login.login"))
        except Exception as e:
            if is_api_request:
                return {"success": False, "error": f"An error occurred: {str(e)}"}, 500
            flash(f"An error occurred: {str(e)}", "error")
        finally:
            db.close()

    return render_template("forgot_password.html")


@login_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    is_api_request = wants_json_response()
    db = get_db()
    try:
        cur = db.cursor()
        cur.execute(
            "SELECT id FROM users WHERE reset_token=? AND reset_token_expiry > ?",
            (token, datetime.now()),
        )
        user = cur.fetchone()

        if not user:
            if is_api_request:
                return {"success": False, "error": "Invalid or expired reset token."}, 400
            flash("Invalid or expired reset token.", "error")
            return redirect(url_for("login.forgot_password"))

        if request.method == "POST":
            data = get_request_data()
            password = data.get("password", "")
            confirm_password = data.get("confirm_password", "")

            if password != confirm_password:
                if is_api_request:
                    return {"success": False, "error": "Passwords do not match."}, 400
                flash("Passwords do not match.", "error")
                return render_template("reset_password.html", token=token)

            hashed_password = generate_password_hash(password)
            cur.execute(
                "UPDATE users SET password=?, reset_token=NULL, reset_token_expiry=NULL WHERE id=?",
                (hashed_password, user[0]),
            )
            db.commit()

            if is_api_request:
                return {
                    "success": True,
                    "message": "Password updated successfully! You can now login.",
                    "redirect": url_for("login.login"),
                }

            flash("Password updated successfully! You can now login.", "success")
            return redirect(url_for("login.login"))

    except Exception as e:
        if is_api_request:
            return {"success": False, "error": f"An error occurred: {str(e)}"}, 500
        flash(f"An error occurred: {str(e)}", "error")
    finally:
        db.close()

    return render_template("reset_password.html", token=token)
