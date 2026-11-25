
import csv
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    ROOT / "ml-training" / "datasets"
    / "PhiUSIIL_Phishing_URL_Dataset.csv"
)

urls = defaultdict(set)
domains = defaultdict(set)

with open(INPUT_FILE, "r", encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        url = (row.get("URL") or "").strip()
        label = (row.get("label") or "").strip()
        domain = (row.get("Domain") or "").strip().lower()

        if url and label:
            urls[url.lower()].add(label)

        if domain and label:
            domains[domain].add(label)

conflicting_urls = {
    url: labels
    for url, labels in urls.items()
    if len(labels) > 1
}

conflicting_domains = {
    domain: labels
    for domain, labels in domains.items()
    if len(labels) > 1
}

print("DATASET AUDIT")
print("Unique normalized URLs:", len(urls))
print("URLs with conflicting labels:", len(conflicting_urls))
print("Unique domains:", len(domains))
print("Domains with mixed labels:", len(conflicting_domains))

print("\nCONFLICTING URL EXAMPLES")

for url, labels in list(conflicting_urls.items())[:10]:
    print(url, "Labels:", labels)
