from flask import Blueprint, request, render_template, redirect, url_for, flash, session
import sqlite3
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
from database import get_db
from datetime import datetime
from routes.email_handler import send_welcome_email
from request_helpers import get_request_data, wants_json_response

register_bp = Blueprint("register", __name__)
load_dotenv()

# Ensure 'gender' column exists in 'users' table
try:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("ALTER TABLE users ADD COLUMN gender TEXT")
    conn.commit()
    conn.close()
    print("Migration completed successfully: Added 'gender' column to 'users' table.")
except Exception:
    # Column likely already exists
    pass


@register_bp.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("recommendation.recommendation"))
    if request.method == "POST":
        is_api_request = wants_json_response()
        data = get_request_data()

        name = data.get("name", "").strip()
        username = data.get("username", "").strip()
        email = data.get("email", "").strip()
        age = str(data.get("age", "")).strip()
        gender = data.get("gender", "").strip()
        password = data.get("password", "")
        repassword = data.get("repassword", "")

        try:
            if int(age) < 18:
                if is_api_request:
                    return {
                        "success": False,
                        "error": "You must be 18 or older to register",
                        "step": 2,
                    }, 400
                flash("Error: You must be 18 or older to register", "error")
                session["reg_form_data"] = dict(data)
                session["reg_error_step"] = 2
                return redirect(url_for("register.register"))
        except ValueError:
            pass

        if password != repassword:
            if is_api_request:
                return {"success": False, "error": "Passwords do not match", "step": 3}, 400
            flash("Error: Passwords do not match", "error")
            session["reg_form_data"] = dict(data)
            session["reg_error_step"] = 3
            return redirect(url_for("register.register"))

        hashed_password = generate_password_hash(password)

        db = get_db()
        try:
            cur = db.cursor()
            cur.execute(
                "INSERT INTO users (name, username, email, password, age, gender, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (name, username, email, hashed_password, age, gender, datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            )
            user_id = cur.lastrowid
            db.commit()

            session["user_id"] = user_id
            session["name"] = name
            session["age"] = int(age) if age.isdigit() else age
            session["gender"] = gender
            session["profile_complete"] = False
            session["can_edit_profile"] = True

            # --- Welcome Email Sending ---
            send_welcome_email(email, name)
            # ---------------------------

            if is_api_request:
                return {
                    "success": True,
                    "message": "Account created successfully!",
                    "redirect": url_for("character_builder.character_builder"),
                }
            flash("Yayyy 🎉 You're in!", "success")
            return redirect(url_for("character_builder.character_builder"))
        except sqlite3.IntegrityError:
            if is_api_request:
                return {"success": False, "error": "Email already exists", "step": 2}, 409
            flash("Error: Email already exists", "error")
            session["reg_form_data"] = dict(data)
            session["reg_error_step"] = 2
            return redirect(url_for("register.register"))
        except Exception as e:
            if is_api_request:
                return {
                    "success": False,
                    "error": f"An error occurred: {str(e)}",
                    "step": 1,
                }, 500
            flash(f"An error occurred: {str(e)}", "error")
            session["reg_form_data"] = dict(data)
            session["reg_error_step"] = 1
            return redirect(url_for("register.register"))
        finally:
            db.close()

    form_data = session.pop("reg_form_data", {})
    error_step = session.pop("reg_error_step", 1)
    return render_template(
        "registration.html", form_data=form_data, error_step=error_step
    )
