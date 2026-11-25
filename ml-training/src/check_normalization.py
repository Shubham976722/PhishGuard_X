
import pandas as pd

df = pd.read_csv(
    "ml-training/datasets/PhiUSIIL_Phishing_URL_Dataset.csv"
)

df["url_exact"] = df["URL"].astype(str).str.strip()
df["url_lower"] = df["url_exact"].str.lower()

exact_duplicates = df["url_exact"].duplicated().sum()
lower_duplicates = df["url_lower"].duplicated().sum()

collision_groups = (
    df.groupby("url_lower")["url_exact"]
    .nunique()
)

case_collisions = collision_groups[collision_groups > 1]

print("=" * 55)
print("URL NORMALIZATION AUDIT")
print("=" * 55)

print("Original records:", len(df))
print("Exact duplicate records:", exact_duplicates)
print("Case-insensitive duplicate records:", lower_duplicates)
print("Case-collision groups:", len(case_collisions))

if len(case_collisions):
    print("\nExamples:")
    print(
        df[df["url_lower"].isin(case_collisions.index)]
        [["URL", "label"]]
        .head(20)
        .to_string(index=False)
    )
