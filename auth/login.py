from flask import Blueprint, request, session, render_template, redirect, url_for, flash, current_app
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
from database import get_db
import secrets
from datetime import datetime, timedelta
import os
from routes.email_handler import send_password_reset_email

login_bp = Blueprint("login", __name__)

load_dotenv()


@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("recommendation.recommendation"))
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        try:
            cur = db.cursor()
            # Allow login via either email or username
            cur.execute(
                "SELECT id, name, password, gender, is_admin FROM users WHERE email=? OR username=?", (email, email)
            )
            user = cur.fetchone()

            if user and check_password_hash(user[2], password):
                session["user_id"] = user[0]
                session["name"] = user[1]
                session["gender"] = user[3] if user[3] else "Not specified"
                session["is_admin"] = bool(user[4])

                # Check if profile is complete (shared logic)
                cur.execute(
                    "SELECT COUNT(*) FROM skin_profile WHERE user_id = ?", (user[0],)
                )
                skin_exists = cur.fetchone()[0] > 0
                cur.execute(
                    "SELECT COUNT(*) FROM hair_profile WHERE user_id = ?", (user[0],)
                )
                hair_exists = cur.fetchone()[0] > 0
                session["profile_complete"] = skin_exists and hair_exists

                flash("Welcome to AyuraAI Control Center! 🛡️" if session["is_admin"] else "Welcome back 🌸 Let's glow!", "success")
                
                # Redirect admins to dashboard, others to recommendations
                if session["is_admin"]:
                    return redirect(url_for("admin.dashboard"))
                return redirect(url_for("recommendation.recommendation"))
            else:
                flash("Invalid email or password", "error")
                return redirect(url_for("login.login"))
        except Exception as e:
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
        email = request.form["email"]
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

                # Send reset email via utility
                reset_url = url_for("login.reset_password", token=token, _external=True)
                if send_password_reset_email(email, reset_url):
                    flash("Reset link sent! Please check your email.", "success")
                else:
                    flash("Failed to send email. There might be a configuration issue.", "error")
            else:
                flash("If that email exists in our system, you will receive a reset link.", "info")
            
            return redirect(url_for("login.login"))
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
        finally:
            db.close()

    return render_template("forgot_password.html")


@login_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    db = get_db()
    try:
        cur = db.cursor()
        cur.execute(
            "SELECT id FROM users WHERE reset_token=? AND reset_token_expiry > ?",
            (token, datetime.now()),
        )
        user = cur.fetchone()

        if not user:
            flash("Invalid or expired reset token.", "error")
            return redirect(url_for("login.forgot_password"))

        if request.method == "POST":
            password = request.form["password"]
            confirm_password = request.form["confirm_password"]

            if password != confirm_password:
                flash("Passwords do not match.", "error")
                return render_template("reset_password.html", token=token)

            hashed_password = generate_password_hash(password)
            cur.execute(
                "UPDATE users SET password=?, reset_token=NULL, reset_token_expiry=NULL WHERE id=?",
                (hashed_password, user[0]),
            )
            db.commit()

            flash("Password updated successfully! You can now login.", "success")
            return redirect(url_for("login.login"))

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
    finally:
        db.close()

    return render_template("reset_password.html", token=token)
