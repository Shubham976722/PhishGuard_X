# PhishGuard X 🛡️

**AI-powered phishing detection, threat intelligence and cybersecurity education platform**

PhishGuard X is a functional academic cybersecurity project that combines URL-based machine learning, external threat intelligence, explainable AI, a local retrieval-augmented generation (RAG) assistant, a React dashboard and a Chrome Manifest V3 extension. It helps users assess suspicious links without automatically blocking websites based on an ML prediction alone.

> **Project status:** Local implementation completed; 152 automated tests passed. Cloud deployment deferred. The ML model operates in advisory mode and is not production-ready.

## Table of contents

- [Features](#features)
- [System architecture](#system-architecture)
- [Technology stack](#technology-stack)
- [Project structure](#project-structure)
- [Installation and local setup](#installation-and-local-setup)
- [Running the project](#running-the-project)
- [Dataset and model training](#dataset-and-model-training)
- [Detection and explainability](#detection-and-explainability)
- [Threat intelligence](#threat-intelligence)
- [Local AI assistant](#local-ai-assistant)
- [Chrome extension](#chrome-extension)
- [API reference](#api-reference)
- [Testing](#testing)
- [Roadmap](#roadmap)
- [Limitations and future work](#limitations-and-future-work)
- [License and attribution](#license-and-attribution)

## Features

- **Hybrid URL analysis:** LightGBM evaluates 17 lexical and structural URL features alongside threat feed matches.
- **Threat intelligence:** Phishing.Database and URLhaus indicators, exact URL hash matching, hostname fallback, provider attribution and expiration tracking.
- **Explainable AI:** LightGBM contribution values explain which features increase or decrease the model's phishing score.
- **Authentication:** JWT-based authentication, password hashing and user-specific scan history.
- **Local AI assistant:** Ollama-powered cybersecurity education using retrieved knowledge-base passages; scan explanations are grounded in stored scan data.
- **React dashboard:** URL scanner, verdict and risk display, scan history, authentication and AI assistant.
- **Chrome extension:** On-demand scanning of the active HTTP(S) tab, toolbar badges, popup results and account settings.
- **Database persistence:** PostgreSQL stores accounts, scans, threat indicators and feed synchronization records.

## System architecture

```mermaid
flowchart TD
    U[User] --> W[React / Vite Dashboard]
    U --> E[Chrome Manifest V3 Extension]
    W --> A[FastAPI REST API]
    E --> A
    A --> J[JWT Authentication]
    A --> S[URL Scan Service]
    A --> R[RAG Assistant]
    S --> F[URL Feature Extraction]
    F --> M[LightGBM Custom V2]
    M --> X[Feature Contributions]
    S --> T[Threat Intelligence Matching]
    M --> V[Advisory Verdict]
    T --> V
    J --> D[(PostgreSQL)]
    S --> D
    T --> D
    P[Phishing.Database] --> I[Feed Sync Service]
    H[URLhaus] --> I
    I --> D
    R --> K[(Local Knowledge Index)]
    R --> N[nomic-embed-text]
    K --> Q[Qwen 2.5 1.5B]
    R --> Q
```

## Technology stack

| Layer | Technologies |
|---|---|
| Backend | Python 3.12, FastAPI, Uvicorn, Pydantic |
| Database | PostgreSQL, SQLAlchemy, Alembic, psycopg |
| Authentication | JWT, PyJWT, pwdlib |
| Machine learning | LightGBM, NumPy, pandas, scikit-learn; Random Forest and XGBoost evaluated during experiments |
| URL parsing | urllib.parse, tldextract, ipaddress, regular expressions |
| Explainability | Native LightGBM prediction contributions (TreeSHAP) |
| Frontend | React, Vite, JavaScript, CSS |
| Browser extension | Chrome Manifest V3, JavaScript, HTML, CSS |
| AI assistant | Ollama, Qwen 2.5 1.5B, nomic-embed-text, local JSON vector index |
| Testing | pytest |
| Development | Git, GitHub, Windows PowerShell, Google Colab |

## Project structure

Key directories and files (not an exhaustive listing):

```text
PhishGuard_X/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── integrations/
│   │   ├── models/
│   │   ├── rag/
│   │   ├── schemas/
│   │   ├── services/
│   │   │   ├── ml_service.py
│   │   │   ├── scan_service.py
│   │   │   └── url_features.py
│   │   ├── database.py
│   │   └── main.py
│   ├── migrations/
│   ├── scripts/
│   └── requirements.txt
├── frontend/
├── browser-extension/
│   ├── manifest.json
│   ├── service_worker.js
│   ├── popup.html
│   ├── popup.js
│   ├── popup.css
│   └── icons/
├── ml-training/
│   ├── src/
│   └── models/
│       └── custom_v2/
│           ├── metadata.json
│           ├── phishguard_model.txt
│           └── phishguard_model.joblib
├── tests/
├── alembic.ini
├── .env.example
├── .gitignore
└── README.md
```

## Installation and local setup

The following commands target Windows PowerShell. Run backend commands from the repository root unless otherwise stated.

### 1. Install prerequisites

- Python 3.12 (project developed with 3.12.10)
- Git
- Node.js 20+ and npm (use a supported version compatible with the frontend lockfile)
- PostgreSQL 16+; PostgreSQL 18 was used in local development
- Google Chrome
- Ollama (optional for scanning; required for local generative assistant functionality)

Verify tools:

```powershell
py -3.12 --version
node --version
npm --version
git --version
```

### 2. Clone the repository

```powershell
git clone https://github.com/Shubham976722/PhishGuard_X.git
cd PhishGuard_X
```

### 3. Create and activate the Python virtual environment

```powershell
py -3.12 -m venv backend\.venv
.\backend\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
python -m pip check
```

If PowerShell prevents activation, use a temporary process-only policy (if allowed by your organization):

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\backend\.venv\Scripts\Activate.ps1
```

Alternatively, run ` .\backend\.venv\Scripts\python.exe` directly without activating the environment.

### 4. Set up PostgreSQL

Start the PostgreSQL service and create the database using pgAdmin or the SQL Shell (`psql`) as an administrative database user:

```sql
CREATE DATABASE phishguard_db;
```

Use a dedicated application database role with appropriate permissions for the database and schema. For local development, configure the credentials for the role you actually created; do not reuse production credentials.

### 5. Configure environment variables

```powershell
Copy-Item .env.example .env
notepad .env
```

Use the exact variable names defined in `.env.example`. Configure the PostgreSQL connection, JWT signing secret, and any optional provider/Ollama settings. A SQLAlchemy connection URI typically has the following form (replace placeholders):

```text
postgresql+psycopg://DB_USER:DB_PASSWORD@localhost:5432/phishguard_db
```

Generate a random JWT secret locally:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Store the generated value in the JWT secret setting defined by the project. Configure a URLhaus API key if you intend to synchronize that provider. Never commit `.env`, passwords, API keys or tokens.

### 6. Apply database migrations

```powershell
python -m alembic upgrade head
python -m alembic current
```

### 7. Verify the pretrained model

```powershell
Get-ChildItem .\ml-training\models\custom_v2
python -c "from backend.app.services.ml_service import predict_url; print(predict_url('https://www.google.com/'))"
```

The native model text file and metadata must be available. The joblib file is retained as a training artifact backup. No retraining is required for normal local execution. Load serialized artifacts only from trusted sources.

### 8. Install frontend dependencies

```powershell
cd frontend
npm install
cd ..
```

If the repository contains a valid package lockfile, `npm ci` is preferable for reproducible installations.

### 9. Set up Ollama (optional)

Install Ollama from <https://ollama.com/download>. Then download the local models:

```powershell
ollama pull qwen2.5:1.5b
ollama pull nomic-embed-text
ollama list
```

Ollama normally runs at `http://localhost:11434`. Model downloads require internet access; inference can run locally after downloads. Verify that the RAG index is present under `backend/app/rag/storage/index.json`. If it is missing, rebuild it using the project's indexing workflow before using the assistant.

## Running the project

Use separate terminals. PostgreSQL must be running before starting the API.

**Terminal 1 — Backend (repository root)**

```powershell
.\backend\.venv\Scripts\Activate.ps1
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

- API: <http://127.0.0.1:8000>
- Swagger UI: <http://127.0.0.1:8000/docs>
- OpenAPI: <http://127.0.0.1:8000/openapi.json>

**Terminal 2 — Frontend**

```powershell
cd frontend
npm run dev
```

Open the URL printed by Vite. The original project setup documents port 3000; use the actual terminal URL if different. Configure the frontend API base URL and backend CORS settings if necessary.

**Terminal 3 — Ollama, if not already running**

```powershell
ollama serve
```

Do not launch another Ollama server if it is already running.

### Verify and use the application

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health/ready
```

Expected health states: `healthy` and `ready` with database `connected`. Register an account in the dashboard, log in, scan a URL, review the explanation and scan history, and open the AI assistant if Ollama is available. Run feed synchronization separately to populate fresh threat intelligence.

## Dataset and model training

### Dataset

The model was developed using the **PhiUSIIL Phishing URL Dataset**, available from the UCI Machine Learning Repository: <https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset>.

The source CSV was `PhiUSIIL_Phishing_URL_Dataset.csv`. It contains legitimate and phishing URLs with precomputed URL and webpage attributes. The deployed model uses only custom URL-derived features, not webpage contents or external lookup features.

| Dataset property | Count |
|---|---:|
| Original rows | 235,795 |
| Original columns | 56 |
| Duplicate URL records removed | 425 |
| Cleaned rows | 235,370 |
| Legitimate URLs | 134,850 |
| Phishing URLs | 100,520 |

Original labels were `0 = phishing`, `1 = legitimate`. For training V2, labels were remapped to `target = 1` for phishing and `target = 0` for legitimate. This convention is recorded in the model metadata.

### Data preparation and splitting

1. Load the dataset in Google Colab using pandas.
2. Audit missing values, duplicate URLs and conflicting labels; remove duplicate URL records.
3. Remap the labels to the phishing-positive convention.
4. Derive registered domains using `tldextract` with the bundled suffix list.
5. Group samples by registered domain before splitting to reduce domain leakage.
6. Verify that training, validation and test sets do not share URL or registered-domain groups.
7. Recompute custom features from raw URL strings rather than relying on incompatible precomputed dataset features.

Final V2 retraining split:

| Split | Legitimate | Phishing | Total |
|---|---:|---:|---:|
| Training | 94,531 | 75,684 | 170,215 |
| Validation | 20,227 | 11,807 | 32,034 |
| Test | 20,092 | 13,029 | 33,121 |
| **Total** | **134,850** | **100,520** | **235,370** |

URL and registered-domain overlap checks returned zero across the three split pairs. This reduces one form of leakage but does not remove dataset collection bias.

### Feature engineering: 17 features

| Feature | Meaning |
|---|---|
| `url_length` | Length of the URL string |
| `hostname_length` | Length of the parsed hostname |
| `path_length` | Length of the URL path |
| `query_length` | Length of the query string |
| `tld_length` | Length of the extracted public suffix |
| `subdomain_count` | Number of subdomain components |
| `letter_count` | Number of ASCII letters |
| `letter_ratio` | ASCII letters divided by URL length |
| `digit_count` | Number of ASCII digits |
| `digit_ratio` | Digits divided by URL length |
| `special_char_count` | Number of characters outside ASCII letters and digits |
| `special_char_ratio` | Special characters divided by URL length |
| `hyphen_count` | Number of hyphens |
| `dot_count` | Number of dots |
| `percent_count` | Number of percent signs |
| `at_count` | Number of at signs |
| `has_ip_address` | Whether the hostname is an IP address |

The feature order is stored in `metadata.json` and must match the native model. The extractor is implemented in `backend/app/services/url_features.py`.

### Training and model selection

Initial experiments compared Random Forest, XGBoost and LightGBM on 10- and 17-feature dataset-derived configurations. LightGBM was selected for further development. A runtime audit found mismatches between some precomputed PhiUSIIL features and live URL extraction, so the final V2 model was retrained using 17 consistently recomputed URL features.

The final training workflow was:

1. Compute custom features for the domain-grouped datasets.
2. Train a binary LightGBM classifier using training data, with validation-based early stopping.
3. Evaluate precision, recall, F1 and other classification metrics; use validation scores for threshold selection.
4. Select the validation F1 threshold and export the best model as a native LightGBM text artifact.
5. Export the joblib backup, feature order and model metadata; integrate the native Booster into FastAPI.
6. Check real URL examples and retain advisory mode because significant false positives remain.

| Final model configuration | Value |
|---|---|
| Model name | `LightGBM_Custom_17` |
| Version | `2.0.0` |
| Training LightGBM version | `4.6.0` |
| Feature count | 17 |
| Configured boosting rounds | 500 |
| Best iteration | 496 |
| Validation F1-selected threshold | `0.7160938213138232` |
| Positive class | Phishing (`1`) |
| Detection mode | Advisory |
| Production ready | No |

### Evaluation results

Final custom V2 model, internal validation set, at the selected threshold (before the later runtime root-slash adjustment):

| Metric | Result |
|---|---:|
| Accuracy | 99.6535% |
| False positives | 9 |
| False negatives | 102 |

These are internal dataset results, not real-world accuracy guarantees. Earlier dataset-derived baseline metrics must not be attributed to the final custom model. A separate hand-picked sanity check incorrectly flagged 9 of 20 legitimate URLs before the root-slash adjustment. A representative external evaluation and final custom-model held-out test metrics are not documented here.

### Model artifacts and reproduction

```text
ml-training/models/custom_v2/
├── phishguard_model.txt       # Native LightGBM Booster used by the API
├── phishguard_model.joblib    # Serialized training backup
└── metadata.json             # Feature order, threshold and version
```

Training was performed in Google Colab. The original dataset and splits were backed up separately; they are not required for running the API. To reproduce training, obtain the source dataset, follow the cleaning, grouping, feature extraction and model selection steps above, and export compatible artifacts. Exact notebook cells, hyperparameters beyond those documented, split seed and notebook availability have not been verified in this README. Existing scripts in `ml-training/src/` include earlier experiments and should not be assumed to reproduce V2 exactly; archived models may need to be restored or regenerated for legacy scripts.

## Detection and explainability

The API combines ML scores with threat intelligence. The raw model classification threshold is separate from the application-level advisory policy.

| Evidence | API verdict | Risk level |
|---|---|---|
| Exact URL match in phishing feed | `phishing` | High |
| Exact URL match in malware feed | `malware` | High |
| Hostname-only threat match | `suspicious` | Medium |
| No threat match; ML probability >= 0.10 | `suspicious` | Medium |
| No threat match; ML probability < 0.10 | `legitimate` | Low |

The returned numerical risk score is the raw ML probability multiplied by 100 and rounded; it is not a calibrated confidence value. Threat intelligence may override the verdict independently of that score. Neither a low score nor the absence of a feed match guarantees safety. Feed matches are evidence reported by external providers, not infallible proof.

LightGBM's native `pred_contrib` output provides signed feature contributions and a bias term on the raw log-odds scale. Positive contributions increase the model's phishing score; negative contributions reduce it. Contributions are not percentages or causal explanations. The RAG assistant does not decide the verdict.

### URL normalization correction

During integration, the API's URL parsing added a trailing slash to root URLs. The model was sensitive to that representation. The feature extractor now removes a root-only slash when no query or fragment is present, preserving non-root paths and actual hostnames. This adjustment affects ML features, not threat intelligence matching.

Local verification after the fix:

| URL | ML score | Raw model classification |
|---|---:|---|
| `https://www.google.com` | 0.19% | Legitimate |
| `https://www.google.com/` | 0.19% | Legitimate |
| `https://google.com` | 99.74% | Phishing (false positive) |
| `https://example.com` | 99.82% | Phishing (false positive) |

The last two are advisory `suspicious` verdicts at API level in the absence of threat matches. The normalization fix does not remove the underlying domain and dataset bias, and it introduces a small inference-versus-training preprocessing difference.

## Threat intelligence

| Provider | Purpose |
|---|---|
| [Phishing.Database](https://github.com/mitchellkrogza/Phishing.Database) | Reported phishing URLs |
| [URLhaus](https://urlhaus.abuse.ch/) | Reported malware-distribution URLs |

Feed synchronization streams or retrieves indicators, validates HTTP(S) URLs, deduplicates entries and upserts them in batches. The database tracks source, threat type, hostname, URL hash, timestamps and expiration. Matching prioritizes exact URL hashes and uses hostnames as weaker evidence. Expired entries are ignored. Multiple matching providers can be retained in scan results.

An earlier local synchronization recorded approximately 790,000 indicators; actual counts change over time. The database is a local snapshot, not a continuous guarantee of current coverage.

### Synchronize feeds

From the repository root with the virtual environment activated:

```powershell
python -m backend.scripts.sync_threat_feeds
```

Internet access and the appropriate provider credentials are required. The full phishing feed may take substantial time to download and process. Synchronization outcomes are recorded in the database. For local use, refresh feeds manually as needed; unattended scheduling is optional.

## Local AI assistant

The assistant uses a local knowledge base of phishing, social engineering and incident response material.

- Embedding model: `nomic-embed-text` (768-dimensional embeddings).
- Generation model: `qwen2.5:1.5b`.
- Retrieval: cosine similarity against the local JSON index, with relevance filtering.
- Default retrieval count: 3; supported range: 1–5.
- Scan-specific explanations use stored scan data and deterministic feature contributions rather than allowing the LLM to invent numerical scores.

The general assistant retrieves relevant passages and returns an answer with source references. An insufficient-context fallback is used when applicable. The assistant provides educational guidance, not autonomous security enforcement. Local generation can be slow on low-memory devices.

Example questions:

- What is phishing and how does it work?
- What should I do after clicking a suspicious link?
- Why was my scanned URL marked suspicious?
- Does a high ML score prove that a website is malicious?

## Chrome extension

### Install locally

1. Start the FastAPI backend on port 8000.
2. Open Chrome and navigate to `chrome://extensions/`.
3. Enable **Developer mode**.
4. Click **Load unpacked**.
5. Select the repository's `browser-extension` directory.
6. Pin PhishGuard X to the browser toolbar.
7. Open the popup settings, configure the local backend URL and log in with a registered account.
8. Open an HTTP(S) website and click the extension to scan the current tab.

### Extension behavior

- Manifest V3 with `activeTab` and `storage` permissions and local API host access.
- Service worker sends the active tab URL to the authenticated scan endpoint.
- Recent results are cached for five minutes.
- Popup shows verdict, ML score, threat match details and explanations.
- Toolbar badges are `SAFE`, `WARN` and `ALERT`; `SAFE` should be interpreted as low detected risk, not a safety guarantee.

The extension is an on-demand scanner, not a full network filter or automatic navigation blocker. Reload it after changing extension files. Latest live badge compatibility with V2 should be verified before claiming full end-to-end coverage.

## API reference

Interactive API documentation: <http://127.0.0.1:8000/docs>.

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| GET | `/` | Root endpoint | No |
| GET | `/api/v1/health` | Liveness | No |
| GET | `/api/v1/health/ready` | Database readiness | No |
| POST | `/api/v1/auth/register` | Register account | No |
| POST | `/api/v1/auth/login` | Obtain JWT access token | No |
| GET | `/api/v1/auth/me` | Current user profile | Yes |
| POST | `/api/v1/scans/` | Scan HTTP(S) URL | Yes |
| GET | `/api/v1/scans/history` | User scan history with pagination | Yes |
| POST | `/api/v1/assistant/ask` | General cybersecurity question | Yes |
| POST | `/api/v1/assistant/ask-scan/{scan_id}` | Explain a user-owned scan | Yes |

### Example scan request

```json
{
  "url": "https://www.google.com/"
}
```

Protected endpoints require `Authorization: Bearer <access_token>`. Use Swagger UI to register, log in, authorize and submit a request. Scan responses include the URL, risk score, risk level, verdict, threat type, match type, threat sources, threat types, explanation and scan timestamp.

### Example assistant request

```json
{
  "question": "What should I do if I clicked a phishing link?",
  "top_k": 3
}
```

### Security considerations

JWT authentication, password hashing and ownership checks protect account-specific operations. Keep secrets outside source control, restrict CORS to intended origins, and use HTTPS and appropriate deployment hardening before exposing the API publicly. The scanner sends submitted URLs to the backend and stores scan history; URLs may contain sensitive query parameters. Avoid submitting private authentication links or confidential URLs.

## Testing

From the project root:

```powershell
.\backend\.venv\Scripts\Activate.ps1
python -m pytest -q --tb=short
```

Latest recorded full-suite output with a numerical count:

```text
152 passed, 2 warnings in 14.83s
```

The warnings were Starlette HTTP 422 constant deprecation warnings. Regression tests were subsequently reported passing after the URL normalization and model cleanup changes.

Test areas include authentication, database sessions, API validation, URL extraction, model integration, scan policy, threat ingestion and matching, assistant retrieval/API behavior and extension manifest validation. Automated tests verify software behavior; they do not establish real-world detection accuracy or complete browser UI compatibility.

Optional frontend build verification:

```powershell
cd frontend
npm run build
```

## Roadmap

| Phase | Scope | Status |
|---:|---|---|
| 1 | Initialization and environment | Complete |
| 2 | Database and migrations | Complete |
| 3 | Authentication and API security | Complete |
| 4 | URL extraction and dataset audit | Complete |
| 5 | ML experiments, selection and V2 integration | Complete (advisory) |
| 6 | Scan service and explainability | Complete |
| 7 | Multi-provider threat intelligence | Complete |
| 8 | Local RAG assistant | Implemented; user-reported live testing |
| 9 | Chrome Manifest V3 extension | Implemented; latest live compatibility not independently verified |
| 10 | React/Vite dashboard | Implemented; live scan reported working |
| 11 | Integration, regression testing and normalization correction | Complete for local academic scope |
| 12 | Docker and cloud deployment | Deferred |

## Limitations and future work

- **Dataset bias:** Legitimate training samples were disproportionately root URLs. Bare domains and legitimate URLs with complex paths can receive high scores.
- **Generalization:** The model has strong internal validation metrics but lacks a documented representative external evaluation. Domain-grouped splitting alone does not eliminate sampling bias.
- **Calibration:** Raw ML probabilities are not calibrated confidence estimates. UI labels should use ML risk score rather than confidence.
- **Threat feed coverage:** New or unreported threats may not appear in local snapshots; stale or incorrect reports are possible.
- **URL-only analysis:** The classifier does not inspect webpage contents, redirects, screenshots, certificate trust or runtime behavior.
- **Extension:** On-demand tab scanning is not continuous protection. Latest V2 badge and popup compatibility remains to be verified.
- **Deployment:** Production hosting, HTTPS, operational monitoring, load testing and independent security assessment are outside the completed local scope.

Future work includes more representative legitimate and phishing data, consistent training/inference canonicalization, external and temporal evaluation, score calibration, UI terminology review and deployment hardening. Do not use this project as the sole basis for a security decision.

## License and attribution

- Project license: MIT, as stated in the original README. Refer to the repository's `LICENSE` file for the actual license text.
- Dataset: [PhiUSIIL Phishing URL Dataset, UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset).
- Threat intelligence: [Phishing.Database](https://github.com/mitchellkrogza/Phishing.Database) and [abuse.ch URLhaus](https://urlhaus.abuse.ch/).
- ML framework: [LightGBM](https://lightgbm.readthedocs.io/).
- Local inference: [Ollama](https://ollama.com/).
- Cybersecurity education sources include CISA, NIST and FTC materials referenced in the local knowledge base.

Review the applicable dataset, model and threat-provider licenses and terms before redistribution or commercial use. Third-party material is not automatically covered by the project's own license.

---

**PhishGuard X** | Computer Engineering academic project | AI-assisted phishing risk assessment and cybersecurity education
