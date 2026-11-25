
import csv
from pathlib import Path
from collections import Counter

DATASET_PATH = (
    Path(__file__).resolve().parents[1]
    / "datasets"
    / "PhiUSIIL_Phishing_URL_Dataset.csv"
)

if not DATASET_PATH.exists():
    raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")

label_counts = Counter()
total_rows = 0
empty_urls = 0
empty_labels = 0
sample_urls = []

with open(DATASET_PATH, "r", encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)

    print("DATASET COLUMNS:")
    print(reader.fieldnames)

    if not reader.fieldnames:
        raise ValueError("CSV headers are missing")

    required = {"URL", "label"}

    if not required.issubset(set(reader.fieldnames)):
        raise ValueError(
            f"Required columns {required} not found."
        )

    for row in reader:
        total_rows += 1

        url = (row.get("URL") or "").strip()
        label = (row.get("label") or "").strip()

        if not url:
            empty_urls += 1

        if not label:
            empty_labels += 1
        else:
            label_counts[label] += 1

        if url and len(sample_urls) < 5:
            sample_urls.append(url)

print("\nDATASET SUMMARY")
print("Total rows:", total_rows)
print("Label distribution:", dict(label_counts))
print("Empty URLs:", empty_urls)
print("Empty labels:", empty_labels)

print("\nSAMPLE URLS")
for url in sample_urls:
    print(url)
