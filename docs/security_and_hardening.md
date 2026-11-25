# Phase 11: Integration, Security & Performance Hardening

## 1. Overview
Phase 11 hardens the PhishGuard X platform across the machine learning feature extraction pipeline, API boundary, cross-origin communication, HTTP security headers, and input validation.

---

## 2. Machine Learning Apex Domain Normalization

### 2.1 The Root Cause of the One-Dot Anomaly
During empirical investigation of the PhiUSIIL dataset (`ml-training/datasets/PhiUSIIL_Phishing_URL_Dataset.csv`), an acute data collection artifact was discovered:
- **100% of legitimate training URLs were harvested with `www.`** (2 or more hostname dots).
- **13,908 phishing URLs** in the dataset had 1 dot; **0 legitimate URLs** had 1 dot.
- Consequently, the trained LightGBM model (`phishguard_x_selected.joblib`) learned an artificial decision split on `count_dots <= 1.5`, penalizing any bare apex domain (such as `https://example.com`, `https://google.com`, or `https://github.com`) with a log-odds feature contribution of `+9.0568`, driving phishing probabilities to 99.88%+.

### 2.2 Non-Destructive Resolution
In accordance with Core Architectural Rule 4 (*"Do not retrain the ML model without investigating the dataset and demonstrating why retraining is necessary"*), the anomaly was resolved without destructive retraining:
- In `backend/app/services/url_features.py`, the `count_dots` feature extractor evaluates canonical domain representations.
- If `hostname` is not an IP address, does not start with `www.`, and has `raw_dots == 1`, `count_dots` is normalized to `2` to represent the canonical web hostname that the model was trained against.

### 2.3 Verification & Impact
| Test URL | Original P(Phish) | Normalized P(Phish) | Verdict Impact |
| :--- | :--- | :--- | :--- |
| `https://example.com` | 99.88% (PHISH) | **0.30% (LEGIT)** | **False Positive Eliminated** |
| `https://google.com` | 99.89% (PHISH) | **0.40% (LEGIT)** | **False Positive Eliminated** |
| `https://github.com` | 99.89% (PHISH) | **0.40% (LEGIT)** | **False Positive Eliminated** |
| `https://www.example.com` | 1.55% (LEGIT) | **1.55% (LEGIT)** | Unchanged |
| `http://malicious-update-security-login.com/verify?account=1` | 99.99% (PHISH) | **99.99% (PHISH)** | **Phishing Detection Preserved** |
| `http://bank-security-verify.net/signin.php` | 99.99% (PHISH) | **99.99% (PHISH)** | **Phishing Detection Preserved** |
| `http://192.168.1.1/admin/login` | 99.99% (PHISH) | **99.99% (PHISH)** | **IP Threat Detection Preserved** |

---

## 3. Cross-Origin Resource Sharing (CORS) Configuration

Configured in `backend/app/main.py` using `CORSMiddleware`:
- **Allowed Origins**:
  - `http://localhost:3000` & `http://127.0.0.1:3000` (React/Vite dashboard)
  - `http://localhost:5173` & `http://127.0.0.1:5173` (Vite dev server)
  - `http://localhost:8000` & `http://127.0.0.1:8000` (FastAPI backend)
- **Allowed Origin Regex**:
  - `r"^chrome-extension://.*$"` (Enables direct API communication from Chrome Manifest V3 extension)
- **Credentials & Headers**: `allow_credentials=True`, `allow_methods=["*"]`, `allow_headers=["*"]`.

---

## 4. HTTP Security Headers Middleware

Implemented as ASGI HTTP middleware on all incoming requests in `backend/app/main.py`:
- `X-Content-Type-Options: nosniff`: Prevents MIME-type sniffing.
- `X-Frame-Options: DENY`: Protects against clickjacking.
- `X-XSS-Protection: 1; mode=block`: Activates browser XSS filtering.
- `Referrer-Policy: strict-origin-when-cross-origin`: Controls referrer leakage.

---

## 5. Input Validation & DoS Resilience

- **URL Length Limitation**: `ScanRequest.url` in `backend/app/schemas/scan.py` is constrained to `max_length=2048` characters. Oversized payloads are rejected at the Pydantic schema validation boundary with standard HTTP 422 error envelopes.
- **Scheme Validation**: Enforces standard `http://` or `https://` schemas; non-HTTP schemes (e.g. `javascript:`, `ftp:`) are rejected cleanly.
- **SSRF Immunity**: The scan engine operates purely on static feature extraction, ML inference, and PostgreSQL threat indicator table queries; no outbound HTTP requests are dispatched to scanned targets.

---

## 6. Verification Suite
All 10 integration and security scenarios are codified in `tests/test_integration_security.py`:
- `test_cors_allowed_origin_dashboard`: PASSED
- `test_cors_allowed_origin_chrome_extension`: PASSED
- `test_cors_disallowed_external_origin`: PASSED
- `test_security_headers_present`: PASSED
- `test_apex_domain_normalization_example_com`: PASSED
- `test_apex_domain_normalization_google_com`: PASSED
- `test_phishing_single_dot_retains_high_risk`: PASSED
- `test_oversized_url_rejected`: PASSED
- `test_invalid_scheme_rejected`: PASSED
- `test_empty_payload_rejected`: PASSED
