
import pandas as pd

df = pd.read_csv(
    "ml-training/datasets/PhiUSIIL_Phishing_URL_Dataset.csv"
)

df["normalized_url"] = (
    df["URL"].astype(str).str.strip().str.lower()
)

duplicate_groups = df.groupby("normalized_url")

conflicts = duplicate_groups["label"].nunique()
conflicts = conflicts[conflicts > 1]

print("=" * 55)
print("DUPLICATE LABEL CONSISTENCY AUDIT")
print("=" * 55)

print("Unique normalized URLs:", df["normalized_url"].nunique())
print("Duplicate records:", df["normalized_url"].duplicated().sum())
print("Conflicting URL groups:", len(conflicts))

if len(conflicts):
    print("\nConflicting examples:")
    print(
        df[df["normalized_url"].isin(conflicts.index)]
        [["URL", "label"]]
        .head(20)
        .to_string(index=False)
    )
else:
    print("\nPASS: No conflicting labels.")

print("\nAudit complete.")
