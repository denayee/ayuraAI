from flask import Blueprint, redirect, url_for, session, flash, request, render_template
from authlib.integrations.flask_client import OAuth
from werkzeug.security import generate_password_hash
from database import get_db
import os
from dotenv import load_dotenv
from routes.email_handler import send_welcome_email

load_dotenv()

google_auth_bp = Blueprint("google_auth", __name__)

# OAuth will be initialized when the blueprint is registered with the app
oauth = OAuth()


def init_google_oauth(app):
    """Initialize Google OAuth with the Flask app."""
    oauth.init_app(app)
    oauth.register(
        name="google",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={
            "scope": "openid email profile",
        },
    )


@google_auth_bp.route("/google/login")
def google_login():
    """Step 1: Redirect user to Google's OAuth login page."""
    redirect_uri = url_for("google_auth.google_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@google_auth_bp.route("/google/callback")
def google_callback():
    """Step 2: Handle Google's redirect back with the authorization code."""
    try:
        # Exchange the authorization code for an access token
        token = oauth.google.authorize_access_token()

        # Get user info from Google
        user_info = token.get("userinfo")
        if not user_info:
            flash("Error: Could not get user info from Google", "error")
            return redirect(url_for("register.register"))

        google_id = user_info["sub"]  # Google's unique user ID
        email = user_info["email"]
        name = user_info.get("name", email.split("@")[0])

        db = get_db()
        try:
            cur = db.cursor()

            # Check if user already exists (by google_id or email)
            cur.execute(
                "SELECT id, name, gender, age FROM users WHERE google_id = ? OR email = ?",
                (google_id, email),
            )
            existing_user = cur.fetchone()

            if existing_user:
                # User exists — log them in
                user_id = existing_user[0]
                user_name = existing_user[1]
                user_gender = existing_user[2] if existing_user[2] else "Not specified"
                user_age = existing_user[3]

                # Update google_id if they signed up with email before
                cur.execute(
                    "UPDATE users SET google_id = ?, auth_provider = 'google' WHERE id = ?",
                    (google_id, user_id),
                )
                db.commit()

                # Set session
                session["user_id"] = user_id
                session["name"] = user_name
                session["gender"] = user_gender

                # Check if profile is complete
                cur.execute(
                    "SELECT COUNT(*) FROM skin_profile WHERE user_id = ?", (user_id,)
                )
                skin_exists = cur.fetchone()[0] > 0
                cur.execute(
                    "SELECT COUNT(*) FROM hair_profile WHERE user_id = ?", (user_id,)
                )
                hair_exists = cur.fetchone()[0] > 0
                session["profile_complete"] = skin_exists and hair_exists

                flash("Welcome back via Google! 🌸", "success")

                # If age/gender are missing, ask for them
                if (
                    not user_gender
                    or user_gender == "Not specified"
                    or not user_age
                    or user_age == 0
                ):
                    return redirect(url_for("google_auth.complete_profile"))

                return redirect(url_for("recommendation.recommendation"))
            else:
                # New user — create account (age=0, gender=None as placeholders)
                cur.execute(
                    """INSERT INTO users (name, username, email, password, age, gender, google_id, auth_provider)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        name,
                        email.split("@")[0],
                        email,
                        generate_password_hash(google_id),
                        0,
                        None,
                        google_id,
                        "google",
                    ),
                )
                user_id = cur.lastrowid
                user_name = name
                db.commit()

                # --- Welcome Email Sending ---
                send_welcome_email(email, name)
                # ---------------------------

                # Set session
                session["user_id"] = user_id
                session["name"] = user_name
                session["gender"] = "Not specified"

                flash("Welcome via Google! 🎉 Just a couple more details...", "success")

                # Redirect to complete profile (age & gender)
                return redirect(url_for("google_auth.complete_profile"))

        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for("register.register"))
        finally:
            db.close()

    except Exception as e:
        flash(f"Google sign-in failed: {str(e)}", "error")
        return redirect(url_for("register.register"))


@google_auth_bp.route("/google/complete-profile", methods=["GET", "POST"])
def complete_profile():
    """Step 3: Collect age & gender from Google users."""
    if "user_id" not in session:
        return redirect(url_for("login.login"))

    if request.method == "POST":
        age = request.form.get("age")
        gender = request.form.get("gender")

        if not age or not gender:
            flash("Please fill in both fields", "error")
            return redirect(url_for("google_auth.complete_profile"))

        try:
            if int(age) < 18:
                flash("Error: You must be 18 or older", "error")
                return redirect(url_for("google_auth.complete_profile"))
        except ValueError:
            flash("Error: Invalid age", "error")
            return redirect(url_for("google_auth.complete_profile"))

        db = get_db()
        try:
            cur = db.cursor()
            cur.execute(
                "UPDATE users SET age = ?, gender = ? WHERE id = ?",
                (age, gender, session["user_id"]),
            )
            db.commit()
            session["gender"] = gender
            flash("Profile complete! 🎉 Let's glow!", "success")
            return redirect(url_for("character_builder.character_builder"))
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for("google_auth.complete_profile"))
        finally:
            db.close()

    return render_template("complete_profile_google.html")
