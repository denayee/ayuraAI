from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database import get_db
from datetime import datetime
from routes.email_handler import send_contact_confirmation_email, send_webinar_registration_email

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/about")
def about():
    return render_template("about.html")


@pages_bp.route("/why-ayuraai")
def why_ayuraai():
    return render_template("why_ayuraai.html")


@pages_bp.route("/user-stories", methods=["GET", "POST"])
def user_stories():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        description = request.form.get("description")
        user_id = session.get("user_id")

        errors = {}
        if not name or len(name) < 2:
            errors["name"] = "Name must be at least 2 characters long."
        if not email or "@" not in email:
            errors["email"] = "Please enter a valid email address."
        if not description or len(description) < 20:
            errors["description"] = "Story description must be at least 20 characters long."

        if errors:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"success": False, "errors": errors}), 400
            for field, msg in errors.items():
                flash(msg, "error")
            return redirect(url_for("pages.user_stories"))

        db = get_db()
        try:
            cur = db.cursor()
            cur.execute(
                "INSERT INTO user_stories (user_id, name, email, description, created_at) VALUES (?, ?, ?, ?, ?)",
                (user_id, name, email, description, datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            )
            db.commit()
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"success": True, "message": "Thank you for sharing your story! It has been submitted for review. ✨"})
            flash("Thank you for sharing your story! ✨", "success")
        except Exception as e:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"success": False, "error": str(e)}), 500
            flash(f"An error occurred: {str(e)}", "error")
        finally:
            db.close()

        return redirect(url_for("pages.user_stories"))

    db = get_db()
    stories = []
    try:
        cur = db.cursor()
        # Use a LEFT JOIN to check if the user exists in the users table
        cur.execute("""
            SELECT s.name, s.description, s.created_at, u.id as user_exists
            FROM user_stories s
            LEFT JOIN users u ON s.user_id = u.id OR s.email = u.email
            ORDER BY s.created_at DESC
        """)
        stories = cur.fetchall()
    except Exception as e:
        print(f"Error fetching stories: {e}")
    finally:
        db.close()

    return render_template("user_stories.html", stories=stories)


@pages_bp.route("/guides")
def guides():
    return render_template("guides.html")


@pages_bp.route("/webinars", methods=["GET", "POST"])
def webinars():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        topic = request.form.get("topic", "AI in Modern Dermatology")
        user_id = session.get("user_id")

        errors = {}
        if not name or len(name) < 2:
            errors["name"] = "Name must be at least 2 characters long."
        if not email or "@" not in email:
            errors["email"] = "Please enter a valid email address."

        if errors:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"success": False, "errors": errors}), 400
            for field, msg in errors.items():
                flash(msg, "error")
            return redirect(url_for("pages.webinars"))

        db = get_db()
        try:
            cur = db.cursor()
            webinar_id = request.form.get("webinar_id")
            if webinar_id:
                webinar_id = int(webinar_id)
            cur.execute(
                "INSERT INTO webinar_registrations (user_id, name, email, webinar_topic, webinar_id, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, name, email, topic, webinar_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            )
            db.commit()

            # --- Webinar Registration Email ---
            try:
                send_webinar_registration_email(email, name, topic)
            except Exception as email_err:
                print(f"Error sending webinar registration email: {email_err}")
            # ----------------------------------

            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"success": True, "message": "Successfully registered for the webinar! We'll send you the link soon. 🚀"})
            flash("Successfully registered! 🚀", "success")
        except Exception as e:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"success": False, "error": str(e)}), 500
            flash(f"An error occurred: {str(e)}", "error")
        finally:
            db.close()

        return redirect(url_for("pages.webinars"))

    db = get_db()
    webinars_list = []
    try:
        cur = db.cursor()
        cur.execute("SELECT * FROM webinars ORDER BY date ASC")
        webinars_list = cur.fetchall()
    except Exception as e:
        print(f"Error fetching webinars: {e}")
    finally:
        db.close()

    return render_template("webinars.html", webinars=webinars_list)


@pages_bp.route("/leadership")
def leadership():
    return render_template("leadership.html")


@pages_bp.route("/partners")
def partners():
    return render_template("partners.html")


@pages_bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        message = request.form.get("message")
        user_id = session.get("user_id")

        errors = {}
        if not name or len(name) < 2:
            errors["name"] = "Name must be at least 2 characters long."
        if not email or "@" not in email:
            errors["email"] = "Please enter a valid email address."
        if not phone or len(phone) < 10:
            errors["phone"] = "Please enter a valid contact number."
        if not message or len(message) < 10:
            errors["message"] = "Message must be at least 10 characters long."

        if errors:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"success": False, "errors": errors}), 400
            for field, msg in errors.items():
                flash(msg, "error")
            return redirect(url_for("pages.contact"))

        db = get_db()
        try:
            cur = db.cursor()
            cur.execute(
                "INSERT INTO support_requests (user_id, name, email, phone, message, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, name, email, phone, message, datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            )
            db.commit()

            # --- Contact Confirmation Email ---
            try:
                # Use a snippet of the message (first 100 chars)
                snippet = message[:100] + "..." if len(message) > 100 else message
                send_contact_confirmation_email(email, name, snippet)
            except Exception as email_err:
                print(f"Error sending contact confirmation email: {email_err}")
            # ----------------------------------

            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"success": True, "message": "Your message has been sent successfully! ✨"})
            flash("Your message has been sent successfully! ✨", "success")
        except Exception as e:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"success": False, "error": str(e)}), 500
            flash(f"An error occurred: {str(e)}", "error")
        finally:
            db.close()

        return redirect(url_for("pages.contact"))

    return render_template("contact.html")
