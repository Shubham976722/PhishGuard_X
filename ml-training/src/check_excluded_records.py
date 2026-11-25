
import pandas as pd

original = pd.read_csv(
    "ml-training/datasets/PhiUSIIL_Phishing_URL_Dataset.csv"
)

processed = pd.read_csv(
    "ml-training/datasets/processed_urls.csv"
)

print("=" * 55)
print("RECORD DIFFERENCE AUDIT")
print("=" * 55)

print("Original records:", len(original))
print("Processed records:", len(processed))
print("Difference:", len(original) - len(processed))

print("\nOriginal label distribution:")
print(original["label"].value_counts())

print("\nProcessed label distribution:")
print(processed["label"].value_counts())

print("\nOriginal missing URLs:", original["URL"].isna().sum())
print("Original missing labels:", original["label"].isna().sum())

print("\nOriginal duplicate URLs:",
      original["URL"].astype(str).str.strip().str.lower().duplicated().sum())

print("\nProcessed duplicate URLs:",
      processed["url"].astype(str).duplicated().sum())

print("\nOriginal invalid labels:",
      (~original["label"].isin([0, 1])).sum())

print("\nOriginal URL scheme distribution:")
print(
    original["URL"].astype(str)
    .str.extract(r"^([a-zA-Z][a-zA-Z0-9+.-]*):")[0]
    .value_counts(dropna=False)
)

print("\nAUDIT COMPLETE")
