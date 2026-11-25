
import csv
import sys
from pathlib import Path
from urllib.parse import urlsplit
from collections import Counter

# Add project root to Python path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.app.services.url_features import extract_url_features

INPUT_FILE = (
    ROOT / "ml-training" / "datasets"
    / "PhiUSIIL_Phishing_URL_Dataset.csv"
)

OUTPUT_FILE = (
    ROOT / "ml-training" / "datasets"
    / "processed_urls.csv"
)

valid_labels = {"0", "1"}
seen_urls = set()
label_counts = Counter()

total = 0
invalid = 0
duplicates = 0

with open(INPUT_FILE, "r", encoding="utf-8-sig", newline="") as source:
    reader = csv.DictReader(source)

    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as output:
        writer = None

        for row in reader:
            total += 1

            url = (row.get("URL") or "").strip()
            label = (row.get("label") or "").strip()

            if label not in valid_labels or not url:
                invalid += 1
                continue

            try:
                parsed = urlsplit(url)

                if (
                    parsed.scheme.lower() not in ("http", "https")
                    or not parsed.hostname
                ):
                    invalid += 1
                    continue

                # Accessing hostname also validates malformed host syntax.
                domain = parsed.hostname.lower()

                features = extract_url_features(url)

            except (ValueError, TypeError):
                invalid += 1
                continue

            normalized_url = url.strip().lower()

            if normalized_url in seen_urls:
                duplicates += 1
                continue

            seen_urls.add(normalized_url)

            record = {
                "url": url,
                "domain": domain,
                **features,
                "label": int(label)
            }

            if writer is None:
                writer = csv.DictWriter(
                    output,
                    fieldnames=record.keys()
                )
                writer.writeheader()

            writer.writerow(record)
            label_counts[label] += 1

print("\nPREPROCESSING COMPLETE")
print("Original records:", total)
print("Invalid records:", invalid)
print("Duplicate records:", duplicates)
print("Processed records:", sum(label_counts.values()))
print("Phishing URLs:", label_counts["0"])
print("Legitimate URLs:", label_counts["1"])
print("Output file:", OUTPUT_FILE)
