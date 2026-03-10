from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from database import get_db

account_bp = Blueprint("account", __name__)


@account_bp.route("/account")
def account():
    if "user_id" not in session:
        return redirect(url_for("login.login"))

    user_id = session["user_id"]
    db = get_db()
    try:
        cur = db.cursor()

        # Get user info
        cur.execute(
            "SELECT name, username, email, age, gender, auth_provider FROM users WHERE id = ?",
            (user_id,),
        )
        user_row = cur.fetchone()

        user_info = {
            "name": user_row[0],
            "username": user_row[1],
            "email": user_row[2],
            "age": user_row[3],
            "gender": user_row[4] or "Not specified",
            "auth_provider": user_row[5] or "local",
        }

        # Get skin profile
        cur.execute(
            "SELECT * FROM skin_profile WHERE user_id = ? ORDER BY id DESC LIMIT 1",
            (user_id,),
        )
        skin_row = cur.fetchone()

        # Get hair profile
        cur.execute(
            "SELECT * FROM hair_profile WHERE user_id = ? ORDER BY id DESC LIMIT 1",
            (user_id,),
        )
        hair_row = cur.fetchone()

        # Get allergies
        cur.execute(
            "SELECT DISTINCT ingredient FROM allergies WHERE user_id = ?", (user_id,)
        )
        allergies = [row[0] for row in cur.fetchall()]

        user_profile = None
        if skin_row and hair_row:
            user_profile = {
                "skin_type": skin_row[3],
                "skin_color": skin_row[4],
                "skin_problems": skin_row[5],
                "sensitivity_level": skin_row[6],
                "oil_level": skin_row[7],
                "acne_presence": skin_row[8],
                "acne_level": skin_row[9],
                "dryness_presence": skin_row[10],
                "dryness_level": skin_row[11],
                "lifestyle": skin_row[12],
                "hair_type": hair_row[3],
                "hair_color": hair_row[4],
                "hair_problems": hair_row[5],
                "scalp_condition": hair_row[6],
                "hair_fall_level": hair_row[7],
                "hair_dryness_presence": hair_row[8],
                "hair_dryness_level": hair_row[9],
                "scalp_itch_presence": hair_row[10],
                "scalp_itch_level": hair_row[11],
                "allergies": ", ".join(allergies) if allergies else "None",
            }

        return render_template(
            "account.html", user_info=user_info, user_profile=user_profile
        )
    finally:
        db.close()


@account_bp.route("/account/update-name", methods=["POST"])
def update_name():
    """AJAX endpoint to update user's full name."""
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Not logged in"}), 401

    data = request.get_json()
    new_name = data.get("name", "").strip() if data else ""

    if not new_name:
        return jsonify({"success": False, "error": "Name cannot be empty"})

    if len(new_name) > 100:
        return jsonify({"success": False, "error": "Name is too long"})

    db = get_db()
    try:
        cur = db.cursor()
        cur.execute(
            "UPDATE users SET name = ? WHERE id = ?",
            (new_name, session["user_id"]),
        )
        db.commit()
        session["name"] = new_name
        return jsonify({"success": True, "name": new_name})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    finally:
        db.close()

