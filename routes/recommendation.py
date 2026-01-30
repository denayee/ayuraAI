from flask import Blueprint, render_template, session, redirect, url_for
import sqlite3

recommendation_bp = Blueprint("recommendation", __name__)


def get_db():
    return sqlite3.connect("database.db")


@recommendation_bp.route("/ai-recommendation")
def recommendation():
    if "user_id" not in session:
        return redirect(url_for("login.login"))

    user_id = session["user_id"]
    db = get_db()
    cur = db.cursor()

    # Check if profile exists
    cur.execute("SELECT COUNT(*) FROM skin_profile WHERE user_id = ?", (user_id,))
    skin_exists = cur.fetchone()[0] > 0

    cur.execute("SELECT COUNT(*) FROM hair_profile WHERE user_id = ?", (user_id,))
    hair_exists = cur.fetchone()[0] > 0

    db.close()

    profile_incomplete = not (skin_exists and hair_exists)

    return render_template(
        "ai_recomadation.html", profile_incomplete=profile_incomplete
    )
