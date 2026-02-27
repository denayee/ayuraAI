from flask import Blueprint, render_template, session, redirect, url_for
from dotenv import load_dotenv
import os
import json
from database import get_db
from routes.ai_implement import generate_recommendation

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

    profile_incomplete = not (skin_exists and hair_exists)

    ai_output = None
    if not profile_incomplete:
        # Define cache file path
        cache_dir = "AI_generated_json_file"
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        cache_file = os.path.join(cache_dir, f"{user_id}.json")

        # Check if cache exists
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r") as f:
                    data = json.load(f)
                    ai_output = data.get("AI_generated_json_file")
            except Exception as e:
                print(f"Error reading cache file: {e}")

        # If no cache or error reading, generate new recommendation
        if ai_output is None:
            # Fetch Skin Profile
            cur.execute(
                "SELECT * FROM skin_profile WHERE user_id = ? ORDER BY id DESC LIMIT 1",
                (user_id,),
            )
            skin_row = cur.fetchone()
            # skin_row indices based on create_db.py:
            # 0:id, 1:user_id, 2:name, 3:skin_type, 4:skin_color, 5:skin_problems,
            # 6:sensitivity_level, 7:oil_level, 8:acne_presence, 9:acne_level,
            # 10:dryness_presence, 11:dryness_level, 12:lifestyle

            # Fetch Hair Profile
            cur.execute(
                "SELECT * FROM hair_profile WHERE user_id = ? ORDER BY id DESC LIMIT 1",
                (user_id,),
            )
            hair_row = cur.fetchone()
            # hair_row indices:
            # 0:id, 1:user_id, 2:name, 3:hair_type, 4:hair_color, 5:hair_problems,
            # 6:scalp_condition, 7:hair_fall_level, 8:dryness_presence, 9:dryness_level,
            # 10:scalp_itch_presence, 11:scalp_itch_level

            # Fetch Allergies
            cur.execute(
                "SELECT ingredient FROM allergies WHERE user_id = ?", (user_id,)
            )
            allergies = [row[0] for row in cur.fetchall()]

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

                # Generate Recommendation
                ai_output = generate_recommendation(user_profile)

                # Save to Cache
                try:
                    with open(cache_file, "w") as f:
                        json.dump(
                            {"user_id": user_id, "AI_generated_json_file": ai_output}, f
                        )
                except Exception as e:
                    print(f"Error saving cache file: {e}")

    db.close()

    return render_template(
        "ai_recomadation.html",
        profile_incomplete2=profile_incomplete,
        ai_output=ai_output,
    )
