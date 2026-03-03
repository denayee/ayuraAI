import pickle
import pandas as pd
from flask import Blueprint, request, render_template

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

    # -------- Skin Features --------
    skin_features = [
        int(request.form["Skin_Color"]),
        int(request.form["Skin_Problems"]),
        int(request.form["Skin_Sensitivity"]),
        int(request.form["Skin_Oil_Level"]),
        int(request.form["Acne"]),
        int(request.form["Skin_Dryness"]),
        int(request.form["Lifestyle"]),
        int(request.form["Age"]),
    ]

    # -------- Hair Features --------
    hair_features = [
        int(request.form["Scalp_Itch"]),
        int(request.form["Hair_Dryness"]),
        int(request.form["Hair_Fall"]),
        int(request.form["Scalp_Condition"]),
        int(request.form["Hair_Problems"]),
        int(request.form["Hair_Color"]),
        int(request.form["Age"]),
    ]

    # -------- Allergy Features --------
    allergy_features = [
        int(request.form["Fragrance_Allergy"]),
        int(request.form["Alcohol_Allergy"]),
        int(request.form["Paraben_Allergy"]),
        int(request.form["Sulfate_Allergy"]),
        int(request.form["Herbal_Allergy"]),
        int(request.form["Nut_Allergy"]),
        int(request.form["Skin_Sensitivity"]),
        int(request.form["Age"]),
    ]

    # -------- Predictions --------
    skin_prediction = skin_model.predict([skin_features])[0]
    hair_prediction = hair_model.predict([hair_features])[0]
    allergy_severity = allergy_model.predict([allergy_features])[0]

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
    if int(request.form["Fragrance_Allergy"]) == 1:
        recommended_products = recommended_products[
            recommended_products["Fragrance_Free"] == 1
        ]

    if int(request.form["Paraben_Allergy"]) == 1:
        recommended_products = recommended_products[
            recommended_products["Paraben_Free"] == 1
        ]

    if int(request.form["Alcohol_Allergy"]) == 1:
        recommended_products = recommended_products[
            recommended_products["Alcohol_Free"] == 1
        ]

    # Select top 5 products
    recommended_products = recommended_products.head(5)

    return render_template(
        "ai_recomadation.html",
        skin=skin_prediction,
        hair=hair_prediction,
        allergy=allergy_severity,
        products=recommended_products.to_dict(orient="records"),
    )
