import pandas as pd
import random

# Number of samples
num_samples = 5000

data = []

# Hair color encoding
# 0 = Black
# 1 = Brown
# 2 = Blonde
# 3 = Red
# 4 = Grey

# Life style encoding
# 0 = indoors
# 1 = outdoors

for _ in range(num_samples):
    age = random.randint(18, 60)
    hair_color = random.randint(0, 4)

    scalp_itch = random.randint(0, 10)
    hair_dryness = random.randint(0, 10)
    hair_fall = random.randint(0, 10)
    scalp_condition = random.randint(0, 10)
    hair_problems = random.randint(0, 10)
    life_style = random.randint(0, 1)

    # ---- Logical Classification Rules ----

    # Oily Hair
    if scalp_condition > 6 and hair_dryness < 4:
        hair_type = "Oily"

    # Dry Hair
    elif hair_dryness > 6 and scalp_itch > 5:
        hair_type = "Dry"

    # Damaged Hair
    elif hair_fall > 6 and hair_problems > 6:
        hair_type = "Damaged"

    # Normal Hair
    else:
        hair_type = "Normal"

    data.append(
        [
            scalp_itch,
            hair_dryness,
            hair_fall,
            scalp_condition,
            hair_problems,
            hair_color,
            hair_type,
            life_style,
            age,
        ]
    )

# Create DataFrame
df = pd.DataFrame(
    data,
    columns=[
        "Scalp_Itch",
        "Hair_Dryness",
        "Hair_Fall",
        "Scalp_Condition",
        "Hair_Problems",
        "Hair_Color",
        "Hair_Type",
        "Life_Style",
        "Age",
    ],
)

# Save to CSV
df.to_csv("D:\AyuraAI-main\Generated_data\hair_dataset.csv", index=False)

print("Hair dataset generated successfully!")
