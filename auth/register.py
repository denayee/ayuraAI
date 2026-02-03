from flask import Blueprint, request, render_template, redirect, url_for, flash, session
import sqlite3
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
from database import get_db

register_bp = Blueprint("register", __name__)
load_dotenv()


@register_bp.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("recommendation.recommendation"))
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        age = request.form["age"]
        password = request.form["password"]
        repassword = request.form["repassword"]

        if password != repassword:
            flash("Error: Passwords do not match", "error")
            return redirect(url_for("register.register"))

        hashed_password = generate_password_hash(password)

        db = get_db()
        try:
            cur = db.cursor()
            cur.execute(
                "INSERT INTO users (name, email, password, age) VALUES (?, ?, ?, ?)",
                (name, email, hashed_password, age),
            )
            user_id = cur.lastrowid
            db.commit()

            session["user_id"] = user_id
            session["name"] = (
                name  # Optimize: Store name in session to avoid extra query in character_builder
            )
            flash("Registration successful! Welcome.", "success")
            return redirect(url_for("character_builder.character_builder"))
        except sqlite3.IntegrityError:
            flash("Error: Email already exists", "error")
            return redirect(url_for("register.register"))
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for("register.register"))
        finally:
            db.close()

    return render_template("registration.html")
