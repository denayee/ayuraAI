from flask import (
    Blueprint,
    render_template,
    session,
    redirect,
    url_for,
    jsonify,
    request,
)
from dotenv import load_dotenv
import os
import json
from database import get_db
from routes.ai_implement import generate_recommendation
from routes.ML_prediction import get_ml_predictions
from routes.product_search import (
    generate_search_query,
    search_all_stores,
)

recommendation_bp = Blueprint("recommendation", __name__)

load_dotenv()


@recommendation_bp.route("/ai-recommendation")
def recommendation():
    if "user_id" not in session:
        return redirect(url_for("login.login"))
    
    # Restrict admins from user-only features
    if session.get('is_admin'):
        return redirect(url_for('admin.dashboard'))
    
    user_id = session["user_id"]
    db = get_db()
    cur = db.cursor()

    # Get User Age and Gender
    cur.execute("SELECT age, gender FROM users WHERE id = ?", (user_id,))
    user_row = cur.fetchone()
    user_age = user_row[0] if user_row else 25
    user_gender = user_row[1] if user_row else "Not specified"

    # Check if profile exists
    cur.execute("SELECT COUNT(*) FROM skin_profile WHERE user_id = ?", (user_id,))
    skin_exists = cur.fetchone()[0] > 0

    cur.execute("SELECT COUNT(*) FROM hair_profile WHERE user_id = ?", (user_id,))
    hair_exists = cur.fetchone()[0] > 0

    profile_incomplete = not (skin_exists and hair_exists)

    # Fetch Skin Profile
    cur.execute(
        "SELECT * FROM skin_profile WHERE user_id = ? ORDER BY id DESC LIMIT 1",
        (user_id,),
    )
    skin_row = cur.fetchone()

    # Fetch Hair Profile
    cur.execute(
        "SELECT * FROM hair_profile WHERE user_id = ? ORDER BY id DESC LIMIT 1",
        (user_id,),
    )
    hair_row = cur.fetchone()

    # Fetch Allergies (DISTINCT to avoid duplicates on re-submission)
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
            "age": user_age,
            "gender": user_gender,
        }

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
        if ai_output is None and user_profile:
            # Generate Recommendation
            ai_output = generate_recommendation(user_profile)

            # Save to Cache
            try:
                cache_data = {}
                if os.path.exists(cache_file):
                    try:
                        with open(cache_file, "r") as f:
                            cache_data = json.load(f)
                    except Exception:
                        pass
                
                cache_data["user_id"] = user_id
                cache_data["AI_generated_json_file"] = ai_output
                
                with open(cache_file, "w") as f:
                    json.dump(cache_data, f)
            except Exception as e:
                print(f"Error saving cache file: {e}")

    # Generate ML recommendations every time (no cache currently implemented for ML)
    ml_predictions = None
    if user_profile:
        ml_predictions = get_ml_predictions(user_profile, user_age)

    db.close()

    return render_template(
        "ai_recomadation.html",
        profile_incomplete2=profile_incomplete,
        ai_output=ai_output,
        ml_data=ml_predictions if not profile_incomplete else None,
        user_profile=user_profile,
    )


@recommendation_bp.route("/api/fetch-products", methods=["POST"])
def fetch_products():
    """Fetch top-rated products from all stores based on user profile.

    Returns: JSON with products from Amazon, Flipkart, and Nykaa
    """
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Not authenticated"}), 401
        
    if session.get('is_admin'):
        return jsonify({"success": False, "error": "Admins cannot perform this action"}), 403

    try:
        data = request.get_json() or {}
        custom_query = data.get("query", "")
        min_rating = data.get("min_rating", 4.0)
        limit_per_store = data.get("limit_per_store", 6)
        offset = data.get("offset", 0)

        # Get user profile from session/database
        user_id = session["user_id"]
        db = get_db()
        cur = db.cursor()

        # Fetch user profile from database
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
            "SELECT DISTINCT ingredient FROM allergies WHERE user_id = ?", (user_id,)
        )
        allergies = [row[0] for row in cur.fetchall()]

        cur.execute("SELECT age, gender FROM users WHERE id = ?", (user_id,))
        user_row = cur.fetchone()
        user_age = user_row[0] if user_row else 25
        user_gender = user_row[1] if user_row else "Not specified"

        db.close()

        # Build user profile
        user_profile = {}
        if skin_row and hair_row:
            user_profile = {
                "skin_type": skin_row[3],
                "skin_color": skin_row[4],
                "skin_problems": skin_row[5],
                "sensitivity_level": skin_row[6],
                "oil_level": skin_row[7],
                "hair_type": hair_row[3],
                "hair_color": hair_row[4],
                "hair_problems": hair_row[5],
                "allergies": ", ".join(allergies) if allergies else "None",
                "age": user_age,
                "gender": user_gender,
            }

        # Generate search query or use custom
        if custom_query:
            search_query = custom_query
        else:
            # Check if query is already cached for user
            user_cache_dir = "AI_generated_json_file"
            user_cache_file = os.path.join(user_cache_dir, f"{user_id}.json")
            cache_data = {}
            search_query = None
            
            if os.path.exists(user_cache_file):
                try:
                    with open(user_cache_file, "r") as f:
                        cache_data = json.load(f)
                        search_query = cache_data.get("search_query")
                except Exception as e:
                    print(f"Error reading AI cache: {e}")
                    
            if not search_query:
                # Generate brand new query from Gemini
                search_query = generate_search_query(user_profile)
                
                # Append to the user's loaded cache file
                cache_data["user_id"] = user_id
                cache_data["search_query"] = search_query
                
                if not os.path.exists(user_cache_dir):
                    os.makedirs(user_cache_dir)
                    
                try:
                    with open(user_cache_file, "w") as f:
                        json.dump(cache_data, f)
                except Exception as e:
                    print(f"Error saving AI cache: {e}")

        # Search ALL stores and get top-rated products with pagination
        result = search_all_stores(search_query, min_rating, limit_per_store, offset, global_timeout=None, user_id=str(user_id))
        all_products = result["products"]
        by_store = result["by_store"]
        has_more = result["has_more"]
        is_exhausted = result["is_exhausted"]
        total = result["total"]

        return jsonify(
            {
                "success": True,
                "query": search_query,
                "products": all_products,
                "by_store": by_store,
                "count": len(all_products),
                "total": total,
                "offset": offset,
                "has_more": has_more,
                "is_exhausted": is_exhausted,
                "amazon_count": len(by_store["amazon"]),
                "flipkart_count": len(by_store["flipkart"]),
                "nykaa_count": len(by_store["nykaa"]),
            }
        )

    except Exception as e:
        print(f"Error fetching products: {e}")
        import traceback

        traceback.print_exc()
        return jsonify(
            {
                "success": False,
                "error": str(e),
                "products": [],
                "has_more": False,
                "is_exhausted": True,
            }
        ), 500
