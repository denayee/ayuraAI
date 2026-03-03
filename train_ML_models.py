import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pickle

# -----------------------------
# 1️⃣ Train Skin Model
# -----------------------------
skin_df = pd.read_csv("Generated_data/skin_dataset_cleaned.csv")

X_skin = skin_df.drop("Skin_Type", axis=1)
y_skin = skin_df["Skin_Type"]

X_train, X_test, y_train, y_test = train_test_split(X_skin, y_skin, test_size=0.2)

skin_model = RandomForestClassifier()
skin_model.fit(X_train, y_train)

print("Skin Model Accuracy:", skin_model.score(X_test, y_test))

pickle.dump(skin_model, open("ML_models/skin_model.pkl", "wb"))


# -----------------------------
# 2️⃣ Train Hair Model
# -----------------------------
hair_df = pd.read_csv("Generated_data/hair_dataset_cleaned.csv")

X_hair = hair_df.drop("Hair_Type", axis=1)
y_hair = hair_df["Hair_Type"]

X_train, X_test, y_train, y_test = train_test_split(X_hair, y_hair, test_size=0.2)

hair_model = RandomForestClassifier()
hair_model.fit(X_train, y_train)

print("Hair Model Accuracy:", hair_model.score(X_test, y_test))

pickle.dump(hair_model, open("ML_models/hair_model.pkl", "wb"))


# -----------------------------
# 3️⃣ Train Allergy Model
# -----------------------------
allergy_df = pd.read_csv("Generated_data/allergy_dataset_cleaned.csv")

X_allergy = allergy_df.drop("Reaction_Severity", axis=1)
y_allergy = allergy_df["Reaction_Severity"]

X_train, X_test, y_train, y_test = train_test_split(X_allergy, y_allergy, test_size=0.2)

allergy_model = RandomForestClassifier()
allergy_model.fit(X_train, y_train)

print("Allergy Model Accuracy:", allergy_model.score(X_test, y_test))

pickle.dump(allergy_model, open("ML_models/allergy_model.pkl", "wb"))

print("All models trained and saved successfully!")
