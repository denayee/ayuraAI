import pandas as pd
import random

num_skin_products = 500
num_hair_products = 500

data = []
product_id = 1

skin_types = ["Oily", "Dry", "Combination", "Sensitive", "Normal"]
hair_types = ["Oily", "Dry", "Normal", "Damaged"]

brands = ["DermaCare", "GlowPlus", "PureSkin", "NatureGlow", "HairVital"]
categories = [
    "Cleanser",
    "Moisturizer",
    "Serum",
    "Shampoo",
    "Conditioner",
    "Oil",
    "Mask",
]

# -----------------------------
# Generate Skin Products
# -----------------------------

for _ in range(num_skin_products):
    skin_type = random.choice(skin_types)
    brand = random.choice(brands)
    category = random.choice(categories)

    for_acne = 1 if skin_type == "Oily" else random.randint(0, 1)
    for_dry_skin = 1 if skin_type == "Dry" else random.randint(0, 1)
    for_sensitive_skin = 1 if skin_type == "Sensitive" else random.randint(0, 1)
    oil_free = 1 if skin_type == "Oily" else random.randint(0, 1)

    data.append(
        [
            product_id,
            f"{brand} {category} {product_id}",
            "Skin",
            brand,
            skin_type,
            for_acne,
            for_dry_skin,
            for_sensitive_skin,
            oil_free,
            "",  # Suitable_Hair_Type (empty for skin product)
            0,
            0,
            0,
            0,  # Hair related
            random.randint(0, 1),  # Fragrance_Free
            random.randint(0, 1),  # Paraben_Free
            random.randint(0, 1),  # Alcohol_Free
            random.randint(0, 1),  # Herbal_Content
            random.randint(0, 1),  # Nut_Content
            random.randint(200, 1500),
            round(random.uniform(3.0, 5.0), 1),
        ]
    )

    product_id += 1


# -----------------------------
# Generate Hair Products
# -----------------------------

for _ in range(num_hair_products):
    hair_type = random.choice(hair_types)
    brand = random.choice(brands)
    category = random.choice(categories)

    for_dandruff = 1 if hair_type == "Oily" else random.randint(0, 1)
    for_hair_fall = 1 if hair_type == "Damaged" else random.randint(0, 1)
    for_dry_hair = 1 if hair_type == "Dry" else random.randint(0, 1)
    sulfate_free = random.randint(0, 1)

    data.append(
        [
            product_id,
            f"{brand} {category} {product_id}",
            "Hair",
            brand,
            "",  # Suitable_Skin_Type
            0,
            0,
            0,
            0,  # Skin related
            hair_type,
            for_dandruff,
            for_hair_fall,
            for_dry_hair,
            sulfate_free,
            random.randint(0, 1),  # Fragrance_Free
            random.randint(0, 1),  # Paraben_Free
            random.randint(0, 1),  # Alcohol_Free
            random.randint(0, 1),  # Herbal_Content
            random.randint(0, 1),  # Nut_Content
            random.randint(200, 1500),
            round(random.uniform(3.0, 5.0), 1),
        ]
    )

    product_id += 1


# -----------------------------
# Create DataFrame
# -----------------------------

columns = [
    "Product_ID",
    "Product_Name",
    "Category",
    "Brand",
    "Suitable_Skin_Type",
    "For_Acne",
    "For_Dry_Skin",
    "For_Sensitive_Skin",
    "Oil_Free",
    "Suitable_Hair_Type",
    "For_Dandruff",
    "For_Hair_Fall",
    "For_Dry_Hair",
    "Sulfate_Free",
    "Fragrance_Free",
    "Paraben_Free",
    "Alcohol_Free",
    "Herbal_Content",
    "Nut_Content",
    "Price",
    "Rating",
]

df = pd.DataFrame(data, columns=columns)
df.to_csv("D:\AyuraAI-main\Generated_data\product_dataset.csv", index=False)

print("Product dataset generated successfully!")
