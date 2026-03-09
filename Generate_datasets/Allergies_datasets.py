import pandas as pd
import random

num_samples = 5000
data = []

for user_id in range(1, num_samples + 1):
    age = random.randint(15, 60)
    skin_sensitivity = random.randint(0, 10)

    # Base allergy probabilities
    fragrance_allergy = 1 if random.random() < 0.25 else 0
    alcohol_allergy = 1 if random.random() < 0.20 else 0
    paraben_allergy = 1 if random.random() < 0.15 else 0
    sulfate_allergy = 1 if random.random() < 0.18 else 0
    herbal_allergy = 1 if random.random() < 0.10 else 0
    nut_allergy = 1 if random.random() < 0.08 else 0

    # Increase allergy chance if sensitivity high
    if skin_sensitivity > 7:
        fragrance_allergy = 1 if random.random() < 0.6 else fragrance_allergy
        alcohol_allergy = 1 if random.random() < 0.5 else alcohol_allergy

    # Count total allergies
    total_allergies = (
        fragrance_allergy
        + alcohol_allergy
        + paraben_allergy
        + sulfate_allergy
        + herbal_allergy
        + nut_allergy
    )

    # Severity Logic
    if total_allergies == 0:
        reaction_severity = 1
    elif total_allergies == 1:
        reaction_severity = random.choice([1, 2])
    elif total_allergies >= 2:
        reaction_severity = random.choice([2, 3])
    else:
        reaction_severity = 1

    data.append(
        [
            user_id,
            fragrance_allergy,
            alcohol_allergy,
            paraben_allergy,
            sulfate_allergy,
            herbal_allergy,
            nut_allergy,
            reaction_severity,
            skin_sensitivity,
            age,
        ]
    )

df = pd.DataFrame(
    data,
    columns=[
        "User_ID",
        "Fragrance_Allergy",
        "Alcohol_Allergy",
        "Paraben_Allergy",
        "Sulfate_Allergy",
        "Herbal_Allergy",
        "Nut_Allergy",
        "Reaction_Severity",
        "Skin_Sensitivity",
        "Age",
    ],
)

df.to_csv("D:\AyuraAI-main\Generated_data\Allergy_dataset.csv", index=False)

print("Allergy dataset generated successfully!")
