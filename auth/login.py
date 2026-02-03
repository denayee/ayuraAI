from flask import Blueprint, request, session, render_template, redirect, url_for, flash
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
from database import get_db

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
            # Select password hash along with id and name
            cur.execute("SELECT id, name, password FROM users WHERE email=?", (email,))
            user = cur.fetchone()

            if user and check_password_hash(user[2], password):
                session["user_id"] = user[0]
                session["name"] = user[1]

                # Check if profile is complete using the SAME connection
                cur = db.cursor()
                cur.execute(
                    "SELECT COUNT(*) FROM skin_profile WHERE user_id = ?", (user[0],)
                )
                skin_exists = cur.fetchone()[0] > 0
                cur.execute(
                    "SELECT COUNT(*) FROM hair_profile WHERE user_id = ?", (user[0],)
                )
                hair_exists = cur.fetchone()[0] > 0
                session["profile_complete"] = skin_exists and hair_exists

                flash("Login successful!", "success")
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
