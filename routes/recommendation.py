from flask import Blueprint, render_template, session, redirect, url_for
from dotenv import load_dotenv
from database import get_db
from ai_implement import get_ai_recommendation

recommendation_bp = Blueprint("recommendation", __name__)

load_dotenv()


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

    ai_output = None
    if not profile_incomplete:
        # Generate AI recommendation if profile is complete
        ai_output = get_ai_recommendation()

    return render_template(
        "ai_recomadation.html",
        profile_incomplete=profile_incomplete,
        ai_output=ai_output,
    )
