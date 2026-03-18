import pickle
import pandas as pd
from flask import Blueprint, request, render_template, jsonify

prediction_bp = Blueprint("prediction", __name__)

# ------------------------------
# Load ML Models
# ------------------------------
skin_model = pickle.load(open("ML_models/skin_model.pkl", "rb"))
hair_model = pickle.load(open("ML_models/hair_model.pkl", "rb"))
allergy_model = pickle.load(open("ML_models/allergy_model.pkl", "rb"))

# Load Product Dataset
products = pd.read_csv("Generated_data/product_dataset_cleaned.csv")


# ------------------------------
# Prediction + Recommendation Route
# ------------------------------
@prediction_bp.route("/predict", methods=["POST"])
def predict():
    payload = request.get_json(silent=True) or {}
    form_data = payload if request.is_json else request.form

    def value(name, default=0):
        return int(form_data.get(name, default))

    # -------- Skin Features --------
    skin_features = [
        value("Skin_Color"),
        value("Skin_Problems"),
        value("Skin_Sensitivity"),
        value("Skin_Oil_Level"),
        value("Acne"),
        value("Skin_Dryness"),
        value("Lifestyle"),
        value("Age"),
    ]

    # -------- Hair Features --------
    hair_features = [
        value("Scalp_Itch"),
        value("Hair_Dryness"),
        value("Hair_Fall"),
        value("Scalp_Condition"),
        value("Hair_Problems"),
        value("Hair_Color"),
        value("Age"),
    ]

    # -------- Allergy Features --------
    allergy_features = [
        value("Fragrance_Allergy"),
        value("Alcohol_Allergy"),
        value("Paraben_Allergy"),
        value("Sulfate_Allergy"),
        value("Herbal_Allergy"),
        value("Nut_Allergy"),
        value("Skin_Sensitivity"),
        value("Age"),
    ]

    # -------- Predictions --------
    try:
        skin_prediction = skin_model.predict([skin_features])[0]
        hair_prediction = hair_model.predict([hair_features])[0]
        allergy_severity = allergy_model.predict([allergy_features])[0]
    except Exception as e:
        print(f"Error in ML prediction: {e}")
        skin_prediction = "Normal"
        hair_prediction = "Normal"
        allergy_severity = 1

    # ------------------------------
    # Product Recommendation Logic
    # ------------------------------

    recommended_products = products[
        (
            (products["Suitable_Skin_Type"] == skin_prediction)
            | (products["Suitable_Hair_Type"] == hair_prediction)
        )
    ]

    # Allergy Filtering
    if value("Fragrance_Allergy") == 1:
        recommended_products = recommended_products[
            recommended_products["Fragrance_Free"] == 1
        ]

    if value("Paraben_Allergy") == 1:
        recommended_products = recommended_products[
            recommended_products["Paraben_Free"] == 1
        ]

    if value("Alcohol_Allergy") == 1:
        recommended_products = recommended_products[
            recommended_products["Alcohol_Free"] == 1
        ]

    # Select top 5 products
    recommended_products = recommended_products.head(5)

    if request.is_json:
        return jsonify(
            {
                "success": True,
                "skin": skin_prediction,
                "hair": hair_prediction,
                "allergy": allergy_severity,
                "products": recommended_products.to_dict(orient="records"),
            }
        )

    return render_template(
        "ai_recomadation.html",
        skin=skin_prediction,
        hair=hair_prediction,
        allergy=allergy_severity,
        products=recommended_products.to_dict(orient="records"),
    )


def get_ml_predictions(user_profile, age):
    """
    Helper function to get ML predictions from the string-based user DB profile.
    Mapping logic matches the dataset generation logic.
    """
    # Defensive defaults
    skin_features = [0, 0, 0, 0, 0, 0, 0, age]
    hair_features = [0, 0, 0, 0, 0, 0, age]
    allergy_features = [0, 0, 0, 0, 0, 0, 0, age]

    # --- Mapping Skin Features ---
    # 0 = Fair, 1 = Medium, 2 = Olive, 3 = Brown, 4 = Dark
    skin_color_map = {"Fair": 0, "Medium": 1, "Olive": 2, "Brown": 3, "Dark": 4}
    skin_color_val = skin_color_map.get(user_profile.get("skin_color", "Medium"), 1)

    # 0 = indoors, 1 = outdoors
    lifestyle_val = 0 if user_profile.get("lifestyle", "Indoor") == "Indoor" else 1

    # Map Low/Med/High & Mild/Moderate/Severe strings to roughly 1-10 scaled values
    def scale_1_to_10(val, is_severity=False):
        if not val:
            return 0
        val = val.lower()
        if "low" in val or "mild" in val:
            return 3
        if "med" in val or "moderate" in val:
            return 6
        if "high" in val or "severe" in val:
            return 9
        return 0

    skin_oil = scale_1_to_10(user_profile.get("oil_level"))
    acne = scale_1_to_10(user_profile.get("acne_level"))
    skin_dryness = scale_1_to_10(user_profile.get("dryness_level"))
    sensitivity = scale_1_to_10(user_profile.get("sensitivity_level"))

    problems = user_profile.get("skin_problems", "")
    skin_problems_count = min(10, len(problems.split(",")) * 2 if problems else 0)

    # 1. Skin_Color | 2. Skin_Problems | 3. Skin_Sensitivity | 4. Skin_Oil_Level | 5. Acne | 6. Skin_Dryness | 7. Lifestyle | 8. Age
    skin_features = [
        skin_color_val,
        skin_problems_count,
        sensitivity,
        skin_oil,
        acne,
        skin_dryness,
        lifestyle_val,
        age,
    ]

    # --- Mapping Hair Features ---
    # 0 = Black, 1 = Brown, 2 = Blonde, 3 = Red, 4 = Grey
    hair_color_map = {
        "Black": 0,
        "Dark Brown": 1,
        "Light Brown": 1,
        "Blonde": 2,
        "Red": 3,
        "Grey/White": 4,
    }
    hair_color_val = hair_color_map.get(user_profile.get("hair_color", "Black"), 0)

    scalp_itch = scale_1_to_10(user_profile.get("scalp_itch_level"))
    hair_dryness = scale_1_to_10(user_profile.get("hair_dryness_level"))
    hair_fall = scale_1_to_10(user_profile.get("hair_fall_level"))

    scalp_cond_map = {"Normal": 5, "Oily": 8, "Dry": 2, "Flaky": 9}
    scalp_condition = scalp_cond_map.get(
        user_profile.get("scalp_condition", "Normal"), 5
    )

    hair_prob = user_profile.get("hair_problems", "")
    hair_problems_count = min(10, len(hair_prob.split(",")) * 2 if hair_prob else 0)

    # 1. Scalp_Itch | 2. Hair_Dryness | 3. Hair_Fall | 4. Scalp_Condition | 5. Hair_Problems | 6. Hair_Color | 7. Age
    hair_features = [
        scalp_itch,
        hair_dryness,
        hair_fall,
        scalp_condition,
        hair_problems_count,
        hair_color_val,
        age,
    ]

    # --- Mapping Allergy Features ---
    allergies = user_profile.get("allergies", "").lower()
    fragrance = 1 if "fragrance" in allergies else 0
    alcohol = 1 if "alcohol" in allergies else 0
    paraben = 1 if "paraben" in allergies else 0
    sulfate = 1 if "sulphates" in allergies else 0
    herbal = 1 if "aloe vera" in allergies else 0
    nut = 1 if "peanuts" in allergies else 0

    # 1. Fragrance | 2. Alcohol | 3. Paraben | 4. Sulfate | 5. Herbal | 6. Nut | 7. Sensitivity | 8. Age
    allergy_features = [
        fragrance,
        alcohol,
        paraben,
        sulfate,
        herbal,
        nut,
        sensitivity,
        age,
    ]

    try:
        skin_prediction = skin_model.predict([skin_features])[0]
        hair_prediction = hair_model.predict([hair_features])[0]
        allergy_severity = allergy_model.predict([allergy_features])[0]
    except Exception as e:
        print("ML Prediction Error:", e)
        skin_prediction = user_profile.get("skin_type", "Normal")
        hair_prediction = user_profile.get("hair_type", "Normal")
        allergy_severity = 1

    # Filter generic product recommendation based on prediction
    recommended_products = products[
        (
            (products["Suitable_Skin_Type"] == skin_prediction)
            | (products["Suitable_Hair_Type"] == hair_prediction)
        )
    ]

    if fragrance == 1:
        recommended_products = recommended_products[
            recommended_products["Fragrance_Free"] == 1
        ]
    if paraben == 1:
        recommended_products = recommended_products[
            recommended_products["Paraben_Free"] == 1
        ]
    if alcohol == 1:
        recommended_products = recommended_products[
            recommended_products["Alcohol_Free"] == 1
        ]

    # Select top 5
    top_products = recommended_products.head(5).to_dict(orient="records")

    return {
        "skin_prediction": skin_prediction,
        "hair_prediction": hair_prediction,
        "allergy_severity": allergy_severity,
        "products": top_products,
    }
