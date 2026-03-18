from flask import Blueprint, request, session, redirect, render_template, url_for, flash
import os
from dotenv import load_dotenv
from database import get_db
from request_helpers import get_request_data, get_request_list, wants_json_response

character_bp = Blueprint("character_builder", __name__)

load_dotenv()


@character_bp.route("/character-builder", methods=["GET", "POST"])
def character_builder():
    is_api_request = request.method == "POST" and wants_json_response()

    if "user_id" not in session:
        if is_api_request:
            return {
                "success": False,
                "error": "You must be logged in to update your profile.",
                "redirect": url_for("login.login"),
            }, 401
        return redirect(url_for("login.login"))

    if not session.get("can_edit_profile"):
        if is_api_request:
            return {
                "success": False,
                "error": "Profile editing is not enabled for this session.",
                "redirect": url_for("account.account"),
            }, 403
        return redirect(url_for("account.account"))

    if "gender" not in session or "age" not in session:
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT gender, age FROM users WHERE id = ?", (session["user_id"],))
        row = cur.fetchone()
        session["gender"] = row[0] if row and row[0] else "Not specified"
        session["age"] = row[1] if row and row[1] else 25
        db.close()

    existing_profile = None
    if request.method == "GET":
        user_id = session["user_id"]
        db = get_db()
        try:
            cur = db.cursor()
            cur.execute(
                "SELECT * FROM skin_profile WHERE user_id = ? ORDER BY id DESC LIMIT 1",
                (user_id,),
            )
            skin_row = cur.fetchone()

            cur.execute(
                "SELECT * FROM hair_profile WHERE user_id = ? ORDER BY id DESC LIMIT 1",
                (user_id,),
            )
            hair_row = cur.fetchone()

            cur.execute(
                "SELECT DISTINCT ingredient FROM allergies WHERE user_id = ?",
                (user_id,),
            )
            allergies = [row[0] for row in cur.fetchall()]

            if skin_row and hair_row:
                existing_profile = {
                    "skin_type": skin_row[3],
                    "skin_color": skin_row[4],
                    "skin_problems": skin_row[5].split(",") if skin_row[5] else [],
                    "sensitivity_level": skin_row[6],
                    "oil_level": skin_row[7],
                    "acne_presence": skin_row[8],
                    "acne_level": skin_row[9],
                    "dryness_presence": skin_row[10],
                    "dryness_level": skin_row[11],
                    "lifestyle": skin_row[12],
                    "hair_type": hair_row[3],
                    "hair_color": hair_row[4],
                    "hair_problems": hair_row[5].split(",") if hair_row[5] else [],
                    "scalp_condition": hair_row[6],
                    "hair_fall_level": hair_row[7],
                    "hair_dryness_presence": hair_row[8],
                    "hair_dryness_level": hair_row[9],
                    "scalp_itch_presence": hair_row[10],
                    "scalp_itch_level": hair_row[11],
                    "allergies": allergies,
                }
        finally:
            db.close()

    if request.method == "POST":
        data = get_request_data()
        user_id = session["user_id"]

        def map_level(value, kind="intensity"):
            if not value:
                return None
            try:
                numeric_value = int(value)
                if kind == "intensity":
                    return {1: "Low", 2: "Medium", 3: "High"}.get(
                        numeric_value, value
                    )
                if kind == "severity":
                    return {1: "Mild", 2: "Moderate", 3: "Severe"}.get(
                        numeric_value, value
                    )
            except ValueError:
                return value
            return value

        skin_type = data.get("skin_type", "")
        skin_color = data.get("skin_color", "")
        skin_problems = ",".join(get_request_list("skin_problems"))
        sensitivity_level = data.get("sensitivity_level", "")
        oil_level = map_level(data.get("oil_level"), "intensity")
        acne_presence = data.get("acne_presence")
        acne_level = (
            map_level(data.get("acne_level"), "severity")
            if acne_presence == "Yes"
            else None
        )
        dryness_presence = data.get("dryness_presence")
        dryness_level = (
            map_level(data.get("dryness_level"), "severity")
            if dryness_presence == "Yes"
            else None
        )
        lifestyle = data.get("lifestyle")

        hair_type = data.get("hair_type", "")
        hair_color = data.get("hair_color", "")
        hair_problems = ",".join(get_request_list("hair_problems"))
        scalp_condition = data.get("scalp_condition", "")
        hair_fall_level = map_level(data.get("hair_fall_level"), "intensity")
        hair_dryness_presence = data.get("hair_dryness_presence")
        hair_dryness_level = (
            map_level(data.get("hair_dryness_level"), "severity")
            if hair_dryness_presence == "Yes"
            else None
        )
        scalp_itch_presence = data.get("scalp_itch_presence")
        scalp_itch_level = (
            map_level(data.get("scalp_itch_level"), "severity")
            if scalp_itch_presence == "Yes"
            else None
        )
        allergies = get_request_list("allergies")

        db = get_db()
        try:
            if "name" in session:
                user_name = session["name"]
            else:
                cur = db.cursor()
                cur.execute("SELECT name FROM users WHERE id = ?", (user_id,))
                user_name = cur.fetchone()[0]

            cur = db.cursor()
            cur.execute(
                """
                INSERT INTO skin_profile
                (user_id, name, skin_type, skin_color, skin_problems, sensitivity_level,
                 oil_level, acne_presence, acne_level, dryness_presence, dryness_level, lifestyle)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    user_name,
                    skin_type,
                    skin_color,
                    skin_problems,
                    sensitivity_level,
                    oil_level,
                    acne_presence,
                    acne_level,
                    dryness_presence,
                    dryness_level,
                    lifestyle,
                ),
            )

            cur.execute(
                """
                INSERT INTO hair_profile
                (user_id, name, hair_type, hair_color, hair_problems, scalp_condition,
                 hair_fall_level, dryness_presence, dryness_level, scalp_itch_presence, scalp_itch_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    user_name,
                    hair_type,
                    hair_color,
                    hair_problems,
                    scalp_condition,
                    hair_fall_level,
                    hair_dryness_presence,
                    hair_dryness_level,
                    scalp_itch_presence,
                    scalp_itch_level,
                ),
            )

            for item in allergies:
                cur.execute(
                    """
                    INSERT INTO allergies (user_id, name, ingredient)
                    VALUES (?, ?, ?)
                    """,
                    (user_id, user_name, item),
                )

            db.commit()
        except Exception as e:
            if is_api_request:
                return {"success": False, "error": f"Failed to save profile: {str(e)}"}, 500
            flash(f"Failed to save profile: {str(e)}", "error")
            return redirect(url_for("character_builder.character_builder"))
        finally:
            db.close()

        session["profile_complete"] = True

        cache_file = os.path.join("AI_generated_json_file", f"{user_id}.json")
        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
            except OSError as e:
                print(f"Error removing cache file: {e}")

        session.pop("can_edit_profile", None)

        if is_api_request:
            return {
                "success": True,
                "message": "Profile updated successfully!",
                "redirect": url_for("recommendation.recommendation"),
            }

        flash("Profile updated successfully!", "success")
        return redirect(url_for("recommendation.recommendation"))

    return render_template("character_builder.html", existing_profile=existing_profile)
