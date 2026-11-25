
import json
import hashlib
from pathlib import Path
from urllib.parse import urlsplit

import pandas as pd
import tldextract

from sklearn.model_selection import GroupShuffleSplit


# ============================================================
# 1. CONFIGURATION
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    ROOT / "ml-training" / "datasets"
    / "processed_urls.csv"
)

OUTPUT_DIR = (
    ROOT / "ml-training" / "datasets"
    / "splits"
)

SEED = 42
CANDIDATES = 300

TRAIN_RATIO = 0.70
VALIDATION_RATIO = 0.15
TEST_RATIO = 0.15

LABEL_COLUMN = "label"

FEATURE_COLUMNS = [
    "url_length",
    "hostname_length",
    "path_length",
    "query_length",
    "count_dots",
    "count_hyphens",
    "count_at",
    "count_digits",
    "count_percent",
    "count_suspicious_words",
    "count_subdirectories",
    "has_https",
    "has_ip_address",
    "has_punycode",
]

EXPECTED_COLUMNS = (
    ["url", "domain"]
    + FEATURE_COLUMNS
    + [LABEL_COLUMN]
)


# Use the locally available Public Suffix List.
# No network download is required.

extractor = tldextract.TLDExtract(
    suffix_list_urls=(),
    include_psl_private_domains=True
)


# ============================================================
# 2. REGISTERED DOMAIN EXTRACTION
# ============================================================

def get_registered_domain(value):

    try:
        value = str(value).strip()

        if "://" in value:
            hostname = urlsplit(value).hostname
        else:
            hostname = urlsplit(
                "//" + value
            ).hostname

        if not hostname:
            raise ValueError("Missing hostname")

        hostname = hostname.lower().rstrip(".")

        # Handle IP addresses separately.
        import ipaddress

        try:
            return str(ipaddress.ip_address(hostname))
        except ValueError:
            pass

        result = extractor(hostname)

        if result.domain and result.suffix:
            return (
                result.domain + "." + result.suffix
            ).lower()

        # Fallback for unusual or private hostnames.
        return hostname

    except (ValueError, TypeError) as error:

        raise ValueError(
            f"Cannot extract registered domain from: {value}"
        ) from error


# ============================================================
# 3. DATASET VERIFICATION
# ============================================================

def verify_dataset(df):

    print("\nDATASET VERIFICATION")
    print("-" * 55)

    if df.empty:
        raise ValueError("Dataset is empty")

    if df.columns.tolist() != EXPECTED_COLUMNS:

        raise ValueError(
            "Dataset columns do not match expected schema.\n"
            f"Expected: {EXPECTED_COLUMNS}\n"
            f"Actual: {df.columns.tolist()}"
        )

    if df.isnull().sum().sum() > 0:
        raise ValueError("Missing values detected")

    if df["url"].duplicated().any():
        raise ValueError("Duplicate URLs detected")

    normalized_urls = (
        df["url"].astype(str).str.strip().str.lower()
    )

    if normalized_urls.duplicated().any():
        raise ValueError(
            "Case-insensitive duplicate URLs detected"
        )

    if not set(df[LABEL_COLUMN].unique()).issubset({0, 1}):
        raise ValueError("Unexpected label values")

    if df[FEATURE_COLUMNS].isna().any().any():
        raise ValueError("Missing feature values")

    if not df[FEATURE_COLUMNS].apply(
        lambda column: pd.api.types.is_numeric_dtype(column)
    ).all():
        raise ValueError("Non-numeric features detected")

    print("PASS: Dataset schema")
    print("PASS: Missing value check")
    print("PASS: Duplicate URL check")
    print("PASS: Label validation")
    print("PASS: Numeric feature validation")

    print("\nDataset records:", len(df))
    print("Feature count:", len(FEATURE_COLUMNS))

    print("\nLabel distribution:")
    print(df[LABEL_COLUMN].value_counts().sort_index())


# ============================================================
# 4. SPLIT SCORING
# ============================================================

def evaluate_split(
    labels,
    selected_indices,
    target_ratio,
    global_phishing_ratio
):

    selected_labels = labels.iloc[selected_indices]

    actual_ratio = (
        len(selected_indices) / len(labels)
    )

    phishing_ratio = selected_labels.eq(0).mean()

    size_error = abs(
        actual_ratio - target_ratio
    )

    class_error = abs(
        phishing_ratio - global_phishing_ratio
    )

    return (
        size_error * 10
        + class_error * 2
    )


# ============================================================
# 5. FIND BEST GROUP-AWARE SPLIT
# ============================================================

def best_group_split(
    frame,
    target_ratio,
    seed_offset
):

    groups = frame["registered_domain"].values

    labels = frame[LABEL_COLUMN]

    global_phishing_ratio = labels.eq(0).mean()

    best_score = float("inf")
    best_selected = None

    splitter = GroupShuffleSplit(
        n_splits=CANDIDATES,
        test_size=target_ratio,
        random_state=SEED + seed_offset
    )

    for _, selected_indices in splitter.split(
        frame,
        labels,
        groups
    ):

        selected_labels = labels.iloc[
            selected_indices
        ]

        # Both classes must exist in every split.
        if selected_labels.nunique() != 2:
            continue

        score = evaluate_split(
            labels,
            selected_indices,
            target_ratio,
            global_phishing_ratio
        )

        if score < best_score:

            best_score = score

            best_selected = selected_indices

    if best_selected is None:

        raise RuntimeError(
            "Unable to generate a valid group split"
        )

    return best_selected, best_score


# ============================================================
# 6. SPLIT SUMMARY
# ============================================================

def split_summary(frame, total_records):

    return {

        "records": int(len(frame)),

        "registered_domains": int(
            frame["registered_domain"].nunique()
        ),

        "phishing": int(
            frame[LABEL_COLUMN].eq(0).sum()
        ),

        "legitimate": int(
            frame[LABEL_COLUMN].eq(1).sum()
        ),

        "phishing_ratio": float(
            frame[LABEL_COLUMN].eq(0).mean()
        ),

        "record_percentage": float(
            len(frame) / total_records * 100
        )
    }


# ============================================================
# 7. MAIN PIPELINE
# ============================================================

def main():

    print("=" * 65)
    print("PHISHGUARD X - DATASET SPLITTING PIPELINE")
    print("=" * 65)

    # --------------------------------------------------------
    # CHECK INPUT
    # --------------------------------------------------------

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Dataset not found: {INPUT_FILE}"
        )

    # Never silently overwrite existing splits.
    if OUTPUT_DIR.exists() and any(OUTPUT_DIR.iterdir()):

        raise FileExistsError(
            f"Split directory already contains files:\n"
            f"{OUTPUT_DIR}\n"
            "Back up or remove existing splits before rerunning."
        )

    # --------------------------------------------------------
    # LOAD DATASET
    # --------------------------------------------------------

    print("\nLoading processed dataset...")

    df = pd.read_csv(INPUT_FILE)

    print("Dataset shape:", df.shape)

    verify_dataset(df)

    # --------------------------------------------------------
    # EXTRACT REGISTERED DOMAINS
    # --------------------------------------------------------

    print("\nExtracting registered domains...")

    df["registered_domain"] = df["url"].apply(
        get_registered_domain
    )

    if df["registered_domain"].isna().any():

        raise ValueError(
            "Missing registered domain detected"
        )

    print(
        "Unique registered domains:",
        df["registered_domain"].nunique()
    )

    # --------------------------------------------------------
    # FIRST SPLIT: TRAIN + VALIDATION / TEST
    # --------------------------------------------------------

    print("\nCreating test dataset...")

    test_indices, test_score = best_group_split(
        df,
        TEST_RATIO,
        seed_offset=0
    )

    test_df = df.iloc[test_indices].copy()

    train_val_df = df.drop(
        df.index[test_indices]
    ).copy()

    # --------------------------------------------------------
    # SECOND SPLIT: TRAIN / VALIDATION
    # --------------------------------------------------------

    print("\nCreating validation dataset...")

    validation_fraction = (
        VALIDATION_RATIO /
        (TRAIN_RATIO + VALIDATION_RATIO)
    )

    validation_indices, validation_score = best_group_split(
        train_val_df,
        validation_fraction,
        seed_offset=1000
    )

    validation_df = train_val_df.iloc[
        validation_indices
    ].copy()

    train_df = train_val_df.drop(
        train_val_df.index[validation_indices]
    ).copy()

    # --------------------------------------------------------
    # VERIFY RECORD COUNTS
    # --------------------------------------------------------

    total_records = (
        len(train_df)
        + len(validation_df)
        + len(test_df)
    )

    if total_records != len(df):

        raise RuntimeError(
            "Dataset record count mismatch"
        )

    # --------------------------------------------------------
    # VERIFY DOMAIN LEAKAGE
    # --------------------------------------------------------

    print("\nVERIFYING DOMAIN LEAKAGE...")
    print("-" * 55)

    train_domains = set(
        train_df["registered_domain"]
    )

    validation_domains = set(
        validation_df["registered_domain"]
    )

    test_domains = set(
        test_df["registered_domain"]
    )

    train_val_overlap = (
        train_domains & validation_domains
    )

    train_test_overlap = (
        train_domains & test_domains
    )

    val_test_overlap = (
        validation_domains & test_domains
    )

    print(
        "Train-Val shared:",
        len(train_val_overlap)
    )

    print(
        "Train-Test shared:",
        len(train_test_overlap)
    )

    print(
        "Val-Test shared:",
        len(val_test_overlap)
    )

    if (
        train_val_overlap
        or train_test_overlap
        or val_test_overlap
    ):

        raise RuntimeError(
            "DOMAIN LEAKAGE DETECTED"
        )

    print("PASS: Zero domain leakage")

    # --------------------------------------------------------
    # VERIFY CLASS DISTRIBUTION
    # --------------------------------------------------------

    for name, frame in [
        ("Training", train_df),
        ("Validation", validation_df),
        ("Testing", test_df)
    ]:

        if frame[LABEL_COLUMN].nunique() != 2:

            raise RuntimeError(
                f"{name} does not contain both classes"
            )

    # --------------------------------------------------------
    # CREATE OUTPUT DIRECTORY
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # SAVE DATASETS
    # --------------------------------------------------------

    train_path = OUTPUT_DIR / "train.csv"

    validation_path = (
        OUTPUT_DIR / "validation.csv"
    )

    test_path = OUTPUT_DIR / "test.csv"

    train_df.to_csv(
        train_path,
        index=False
    )

    validation_df.to_csv(
        validation_path,
        index=False
    )

    test_df.to_csv(
        test_path,
        index=False
    )

    # --------------------------------------------------------
    # CREATE MANIFEST
    # --------------------------------------------------------

    manifest = {

        "project": "PhishGuard X",

        "random_seed": SEED,

        "candidate_splits": CANDIDATES,

        "target_distribution": {
            "train": TRAIN_RATIO,
            "validation": VALIDATION_RATIO,
            "test": TEST_RATIO
        },

        "dataset_sha256": hashlib.sha256(
            INPUT_FILE.read_bytes()
        ).hexdigest(),

        "total_records": len(df),

        "feature_columns": FEATURE_COLUMNS,

        "label_mapping": {
            "0": "phishing",
            "1": "legitimate"
        },

        "splits": {

            "train": split_summary(train_df, len(df)),

            "validation": split_summary(validation_df, len(df)),

            "test": split_summary(test_df, len(df))
        },

        "domain_leakage": {

            "train_validation": len(train_val_overlap),

            "train_test": len(train_test_overlap),

            "validation_test": len(val_test_overlap)
        },

        "split_scores": {

            "test": float(test_score),

            "validation": float(validation_score)
        }
    }

    manifest_path = (
        OUTPUT_DIR / "manifest.json"
    )

    with open(
        manifest_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            manifest,
            file,
            indent=4
        )

    # --------------------------------------------------------
    # FINAL REPORT
    # --------------------------------------------------------

    print("\n" + "=" * 65)
    print("DATASET SPLIT REPORT")
    print("=" * 65)

    for name, frame in [
        ("TRAINING", train_df),
        ("VALIDATION", validation_df),
        ("TESTING", test_df)
    ]:

        print(f"\n{name}")
        print("-" * 45)

        print("Records:", len(frame))

        print(
            "Registered domains:",
            frame["registered_domain"].nunique()
        )

        print(
            "Phishing:",
            int(frame[LABEL_COLUMN].eq(0).sum())
        )

        print(
            "Legitimate:",
            int(frame[LABEL_COLUMN].eq(1).sum())
        )

        print(
            "Phishing ratio:",
            round(
                frame[LABEL_COLUMN].eq(0).mean(),
                4
            )
        )

        print(
            "Percentage:",
            round(
                len(frame) / len(df) * 100,
                2
            ),
            "%"
        )

    print("\nSAVED FILES")
    print("-" * 45)

    print(train_path)
    print(validation_path)
    print(test_path)
    print(manifest_path)

    print("\n" + "=" * 65)
    print("ALL SPLIT CHECKS PASSED")
    print("=" * 65)


if __name__ == "__main__":
    main()
