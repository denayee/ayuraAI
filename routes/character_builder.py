from flask import Blueprint, request, session, redirect, render_template, url_for, flash
from dotenv import load_dotenv
from database import get_db

character_bp = Blueprint("character_builder", __name__)

load_dotenv()


@character_bp.route("/character-builder", methods=["GET", "POST"])
def character_builder():
    # 🔐 Protect route (user must be logged in)
    if "user_id" not in session:
        return redirect(url_for("login.login"))

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

        flash("Profile created successfully!", "success")
        return redirect(url_for("recommendation.recommendation"))

    return render_template("character_builder.html")
