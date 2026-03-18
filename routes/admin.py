from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from database import get_db
from datetime import datetime
from routes.email_handler import send_close_inquiry_email, send_reopen_inquiry_email
from request_helpers import get_request_data, wants_json_response

admin_bp = Blueprint("admin", __name__)


def is_admin():
    return session.get("is_admin")


@admin_bp.before_request
def check_admin():
    if not is_admin():
        if request.method == "POST" and wants_json_response():
            return jsonify({"success": False, "error": "Unauthorized"}), 403
        return redirect(url_for("home"))


@admin_bp.route("/admin")
def dashboard():
    db = get_db()
    try:
        cur = db.cursor()

        cur.execute("SELECT * FROM support_requests ORDER BY created_at DESC")
        support_requests = cur.fetchall()

        cur.execute(
            """
            SELECT
                u.id, u.name, u.email, u.created_at, u.age, u.gender, u.username,
                s.skin_type, s.skin_problems, s.sensitivity_level, s.oil_level,
                h.hair_type, h.hair_problems, h.scalp_condition,
                GROUP_CONCAT(a.ingredient, ', ') as allergies
            FROM users u
            LEFT JOIN skin_profile s ON u.id = s.user_id
            LEFT JOIN hair_profile h ON u.id = h.user_id
            LEFT JOIN allergies a ON u.id = a.user_id
            WHERE u.is_admin = 0
            GROUP BY u.id
            ORDER BY u.created_at DESC
            """
        )
        users = cur.fetchall()

        user_list = []
        columns = [column[0] for column in cur.description]
        for row in users:
            user_list.append(dict(zip(columns, row)))

        cur.execute("SELECT * FROM user_stories ORDER BY created_at DESC")
        stories = cur.fetchall()

        cur.execute("SELECT * FROM webinar_registrations ORDER BY created_at DESC")
        webinars = cur.fetchall()

        cur.execute("SELECT * FROM webinars ORDER BY date ASC")
        scheduled_webinars = cur.fetchall()

        return render_template(
            "admin_dashboard.html",
            support_requests=support_requests,
            users=user_list,
            stories=stories,
            webinars=webinars,
            scheduled_webinars=scheduled_webinars,
        )
    except Exception as e:
        print(f"Admin Dashboard Error: {e}")
        return "An error occurred", 500
    finally:
        db.close()


@admin_bp.route("/admin/webinar/add", methods=["POST"])
def add_webinar():
    is_api_request = wants_json_response()
    data = get_request_data()
    topic = data.get("topic", "").strip()
    description = data.get("description", "").strip()
    date = data.get("date", "").strip()
    time = data.get("time", "").strip()

    db = get_db()
    try:
        db.execute(
            "INSERT INTO webinars (topic, description, date, time, created_at) VALUES (?, ?, ?, ?, ?)",
            (topic, description, date, time, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        db.commit()
        if is_api_request:
            return jsonify(
                {"success": True, "message": "Webinar scheduled successfully!"}
            )
        flash("Webinar added successfully!", "success")
        return redirect(url_for("admin.dashboard"))
    except Exception as e:
        if is_api_request:
            return jsonify({"success": False, "error": str(e)}), 500
        flash(f"Error adding webinar: {e}", "error")
        return redirect(url_for("admin.dashboard"))
    finally:
        db.close()


@admin_bp.route("/admin/webinar/<int:webinar_id>/delete", methods=["POST"])
def delete_webinar(webinar_id):
    db = get_db()
    try:
        db.execute("DELETE FROM webinar_registrations WHERE webinar_id = ?", (webinar_id,))
        db.execute("DELETE FROM webinars WHERE id = ?", (webinar_id,))
        db.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@admin_bp.route("/admin/support/<int:request_id>/status", methods=["POST"])
def update_support_status(request_id):
    payload = request.get_json(silent=True) or {}
    status = payload.get("status")

    db = get_db()
    try:
        cur = db.cursor()
        cur.execute(
            "SELECT name, email, message, status FROM support_requests WHERE id = ?",
            (request_id,),
        )
        support_req = cur.fetchone()
        old_status = support_req[3] if support_req else None

        db.execute(
            "UPDATE support_requests SET status = ? WHERE id = ?",
            (status, request_id),
        )
        db.commit()

        if status == "completed" and support_req:
            try:
                name, email, message, _ = support_req
                snippet = message[:100] + "..." if len(message) > 100 else message
                send_close_inquiry_email(email, name, snippet)
            except Exception as email_err:
                print(f"Error sending close inquiry email: {email_err}")
        elif status == "pending" and old_status == "completed" and support_req:
            try:
                name, email, message, _ = support_req
                snippet = message[:100] + "..." if len(message) > 100 else message
                send_reopen_inquiry_email(email, name, snippet)
            except Exception as email_err:
                print(f"Error sending re-open inquiry email: {email_err}")

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@admin_bp.route("/admin/user/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    db = get_db()
    try:
        cur = db.cursor()
        cur.execute("SELECT is_admin FROM users WHERE id = ?", (user_id,))
        user = cur.fetchone()
        if user and user[0] == 1:
            return (
                jsonify({"success": False, "error": "Cannot delete admin accounts."}),
                403,
            )

        db.execute("DELETE FROM users WHERE id = ?", (user_id,))
        db.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@admin_bp.route("/admin/story/<int:story_id>/delete", methods=["POST"])
def delete_story(story_id):
    db = get_db()
    try:
        db.execute("DELETE FROM user_stories WHERE id = ?", (story_id,))
        db.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@admin_bp.route("/admin/webinar-reg/<int:reg_id>/delete", methods=["POST"])
def delete_webinar_reg(reg_id):
    db = get_db()
    try:
        db.execute("DELETE FROM webinar_registrations WHERE id = ?", (reg_id,))
        db.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()
