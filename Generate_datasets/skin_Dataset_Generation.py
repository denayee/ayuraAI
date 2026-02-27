import pandas as pd
import random

num_samples = 5000
data = []

# Target distribution (balanced)
skin_types = ["Oily", "Dry", "Combination", "Sensitive", "Normal"]
samples_per_type = num_samples // len(skin_types)

for skin_type in skin_types:
    for _ in range(samples_per_type):
        age = random.randint(15, 60)
        skin_color = random.randint(0, 4)
        lifestyle = random.randint(0, 3)

        # Initialize features
        skin_oil = 0
        skin_dryness = 0
        acne = 0
        sensitivity = 0
        skin_problems = 0

        # Logical Feature Assignment
        if skin_type == "Oily":
            skin_oil = random.randint(7, 10)
            skin_dryness = random.randint(0, 3)
            acne = random.randint(5, 10)
            sensitivity = random.randint(3, 6)
            skin_problems = random.randint(4, 8)

        elif skin_type == "Dry":
            skin_oil = random.randint(0, 3)
            skin_dryness = random.randint(7, 10)
            acne = random.randint(0, 4)
            sensitivity = random.randint(5, 8)
            skin_problems = random.randint(3, 7)

        elif skin_type == "Sensitive":
            skin_oil = random.randint(3, 6)
            skin_dryness = random.randint(4, 7)
            acne = random.randint(2, 6)
            sensitivity = random.randint(8, 10)
            skin_problems = random.randint(6, 10)

        elif skin_type == "Combination":
            skin_oil = random.randint(4, 7)
            skin_dryness = random.randint(4, 7)
            acne = random.randint(3, 6)
            sensitivity = random.randint(3, 6)
            skin_problems = random.randint(3, 6)

        else:  # Normal
            skin_oil = random.randint(3, 6)
            skin_dryness = random.randint(3, 6)
            acne = random.randint(0, 4)
            sensitivity = random.randint(2, 5)
            skin_problems = random.randint(2, 5)

        data.append(
            [
                skin_type,
                skin_color,
                skin_problems,
                sensitivity,
                skin_oil,
                acne,
                skin_dryness,
                lifestyle,
                age,
            ]
        )

# Create DataFrame
df = pd.DataFrame(
    data,
    columns=[
        "Skin_Type",
        "Skin_Color",
        "Skin_Problems",
        "Skin_Sensitivity",
        "Skin_Oil_Level",
        "Acne",
        "Skin_Dryness",
        "Lifestyle",
        "Age",
    ],
)

df.to_csv("D:\AyuraAI-main\Generated_data\skin_dataset.csv", index=False)

print("Advanced Skin dataset generated successfully!")
