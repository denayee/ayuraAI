from flask import Blueprint, request, session, redirect, render_template, url_for, flash
import sqlite3

character_bp = Blueprint("character_builder", __name__)


def get_db():
    return sqlite3.connect("database.db")


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

        # ---------- HAIR DATA ----------
        hair_type = request.form["hair_type"]
        hair_color = request.form["hair_color"]
        hair_problems = ",".join(request.form.getlist("hair_problems"))
        scalp_condition = request.form["scalp_condition"]

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
            (user_id, name, skin_type, skin_color, skin_problems, sensitivity_level)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                user_id,
                user_name,
                skin_type,
                skin_color,
                skin_problems,
                sensitivity_level,
            ),
        )

        # Insert hair profile
        cur.execute(
            """
            INSERT INTO hair_profile
            (user_id, name, hair_type, hair_color, hair_problems, scalp_condition)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (user_id, user_name, hair_type, hair_color, hair_problems, scalp_condition),
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


# just try
