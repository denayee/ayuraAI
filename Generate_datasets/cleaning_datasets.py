import pandas as pd


def clean_dataset(input_file, output_file, drop_columns=None):
    print(f"\nCleaning {input_file} ...")

    # Load dataset
    df = pd.read_csv(input_file)

    print("Original Shape:", df.shape)

    # 1️⃣ Remove Exact Duplicate Rows
    df = df.drop_duplicates()

    # 2️⃣ Remove Duplicate Product_ID (if exists)
    if "Product_ID" in df.columns:
        df = df.drop_duplicates(subset=["Product_ID"])

    # 3️⃣ Remove Columns Not Needed
    if drop_columns:
        df = df.drop(columns=drop_columns, errors="ignore")

    # 4️⃣ Remove Columns With Only One Unique Value
    for col in df.columns:
        if df[col].nunique() <= 1:
            df = df.drop(columns=[col])

    # 5️⃣ Remove Rows With Too Many Missing Values
    df = df.dropna(thresh=len(df.columns) - 2)

    # 6️⃣ Fill Remaining Missing Numeric Values
    for col in df.select_dtypes(include=["int64", "float64"]).columns:
        df[col] = df[col].fillna(df[col].median())

    # 7️⃣ Reset Index
    df = df.reset_index(drop=True)

    print("Cleaned Shape:", df.shape)

    # Save cleaned dataset
    df.to_csv(output_file, index=False)
    print(f"Saved cleaned file as {output_file}")


# Clean Skin Dataset
clean_dataset(
    "D:\AyuraAI-main\Generated_data\skin_dataset.csv",
    "D:\AyuraAI-main\Generated_data\skin_dataset_cleaned.csv",
)

# Clean Hair Dataset
clean_dataset(
    "D:\AyuraAI-main\Generated_data\hair_dataset.csv",
    "D:\AyuraAI-main\Generated_data\hair_dataset_cleaned.csv",
)

# Clean Allergy Dataset
clean_dataset(
    "D:\AyuraAI-main\Generated_data\Allergy_dataset.csv",
    "D:\AyuraAI-main\Generated_data\Allergy_dataset_cleaned.csv",
)

# Clean Product Dataset
clean_dataset(
    "D:\AyuraAI-main\Generated_data\product_dataset.csv",
    "D:\AyuraAI-main\Generated_data\product_dataset_cleaned.csv",
)
