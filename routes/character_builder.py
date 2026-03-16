from flask import Blueprint, request, session, redirect, render_template, url_for, flash
import os
from dotenv import load_dotenv
from database import get_db

character_bp = Blueprint("character_builder", __name__)

load_dotenv()


@character_bp.route("/character-builder", methods=["GET", "POST"])
def character_builder():
    # 🔐 Protect route (user must be logged in)
    if "user_id" not in session:
        return redirect(url_for("login.login"))

    # 🔐 User must click Edit Profile button to access this page
    if not session.get("can_edit_profile"):
        return redirect(url_for("account.account"))

    # Ensure gender and age are in session (may be missing for users logged in before this was added)
    if "gender" not in session or "age" not in session:
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT gender, age FROM users WHERE id = ?", (session["user_id"],))
        row = cur.fetchone()
        session["gender"] = row[0] if row and row[0] else "Not specified"
        session["age"] = row[1] if row and row[1] else 25
        db.close()

    # Fetch existing profile data for editing (GET request)
    existing_profile = None
    if request.method == "GET":
        user_id = session["user_id"]
        db = get_db()
        try:
            cur = db.cursor()

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
        user_id = session["user_id"]

        # ---------- SKIN DATA ----------
        skin_type = request.form["skin_type"]
        skin_color = request.form["skin_color"]
        skin_problems = ",".join(request.form.getlist("skin_problems"))
        sensitivity_level = request.form["sensitivity_level"]

        # Helper to map 1-3 to Low/Med/High or Mild/Mod/Sev
        def map_level(value, type="intensity"):
            if not value:
                return None
            try:
                val_int = int(value)
                if type == "intensity":  # Low, Medium, High
                    return {1: "Low", 2: "Medium", 3: "High"}.get(val_int, value)
                elif type == "severity":  # Mild, Moderate, Severe
                    return {1: "Mild", 2: "Moderate", 3: "Severe"}.get(val_int, value)
            except ValueError:
                return value
            return value

        # New Skin Fields
        oil_level = map_level(request.form.get("oil_level"), "intensity")
        acne_presence = request.form.get("acne_presence")
        acne_level = (
            map_level(request.form.get("acne_level"), "severity")
            if acne_presence == "Yes"
            else None
        )
        dryness_presence = request.form.get("dryness_presence")
        dryness_level = (
            map_level(request.form.get("dryness_level"), "severity")
            if dryness_presence == "Yes"
            else None
        )
        lifestyle = request.form.get("lifestyle")

        # ---------- HAIR DATA ----------
        hair_type = request.form["hair_type"]
        hair_color = request.form["hair_color"]
        hair_problems = ",".join(request.form.getlist("hair_problems"))
        scalp_condition = request.form["scalp_condition"]

        # New Hair Fields
        hair_fall_level = map_level(request.form.get("hair_fall_level"), "intensity")
        hair_dryness_presence = request.form.get("hair_dryness_presence")
        hair_dryness_level = (
            map_level(request.form.get("hair_dryness_level"), "severity")
            if hair_dryness_presence == "Yes"
            else None
        )
        scalp_itch_presence = request.form.get("scalp_itch_presence")
        scalp_itch_level = (
            map_level(request.form.get("scalp_itch_level"), "severity")
            if scalp_itch_presence == "Yes"
            else None
        )

        # ---------- ALLERGIES ----------
        allergies = request.form.getlist("allergies")

        db = get_db()

        if "name" in session:
            user_name = session["name"]
        else:
            # Fallback if name not in session (fetch from DB)
            cur = db.cursor()
            cur.execute("SELECT name FROM users WHERE id = ?", (user_id,))
            user_name = cur.fetchone()[0]

        cur = db.cursor()

        # Insert skin profile
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

        # Insert hair profile
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

        # Insert allergies (multi-select)
        for item in allergies:
            cur.execute(
                """
                INSERT INTO allergies (user_id, name, ingredient)
                VALUES (?, ?, ?)
            """,
                (user_id, user_name, item),
            )

        db.commit()
        db.close()

        session["profile_complete"] = True

        # Cache Invalidation: Delete existing recommendation file if it exists
        cache_file = os.path.join("AI_generated_json_file", f"{user_id}.json")
        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
            except OSError as e:
                print(f"Error removing cache file: {e}")

        flash("Profile updated successfully!", "success")
        # Reset the flag so user must click Edit Profile button again
        session.pop("can_edit_profile", None)
        return redirect(url_for("recommendation.recommendation"))

    return render_template("character_builder.html", existing_profile=existing_profile)
