# PhishGuard X — Cybersecurity Assistant & RAG Architecture

## 1. Role & Architectural Boundaries

> [!IMPORTANT]
> **Strict Operational Rule**:
> The Cybersecurity Assistant and RAG pipeline **NEVER** classify or determine whether a URL is phishing, malware, or safe.
> Security verdicts and risk scores are determined solely by:
> 1. The Machine Learning Engine (`backend/app/services/ml_service.py`)
> 2. The Threat Intelligence System (`backend/app/services/threat_match_service.py`)
> 
> The Assistant's sole purpose is to explain scan results, answer general cybersecurity knowledge questions, and provide grounded safety advice.

---

## 2. Infrastructure & Local Model Prerequisites

The assistant is built for 100% private, local execution without sending sensitive browsing data or telemetry to external third-party cloud LLM APIs.

### Ollama Configuration
* **Service Host**: `http://localhost:11434`
* **Embedding Model**: `nomic-embed-text:latest` (137M parameters, 768-dimensional embeddings)
* **Generation Model**: `qwen2.5:1.5b` (1.5B parameters, Q4_K_M quantization)

### Installation & Model Setup Commands
To download and start the required local models, run:
```powershell
ollama pull nomic-embed-text
ollama pull qwen2.5:1.5b
```

---

## 3. Knowledge Base & Document Ingestion

### Knowledge Store
Domain-expert security reference documents are stored in Markdown format inside:
`backend/app/rag/documents/`
* `phishing_basics.md`: Fundamentals of phishing attacks, spear phishing, credential harvesting.
* `phishing_and_social_engineering.md`: Common social engineering tactics, urgency triggers, spoofing.
* `phishing_incident_response.md`: Step-by-step guidance on responding to suspected credential theft.

### Ingestion Pipeline
Text documents are chunked with the following parameters:
* **Chunk Size**: `900` characters
* **Chunk Overlap**: `150` characters (preserves boundary context)
* **Word Boundary Snapping**: Chunks break on word boundaries rather than slicing mid-word.

### Rebuilding the Index
To re-index documents whenever knowledge files are added or modified, run:
```powershell
$env:PYTHONPATH="."
& backend\.venv\Scripts\python.exe backend/scripts/ingest_rag_docs.py
```
The resulting vector embeddings and chunk metadata are saved to:
`backend/app/rag/storage/index.json`

---

## 4. Retrieval & Generation Pipeline

1. **Retrieval**:
   * Generates a 768-dimensional query vector via `nomic-embed-text`.
   * Computes normalized cosine similarity against all chunks in `index.json`.
   * Ranks candidates and filters out chunks below `MIN_SIMILARITY = 0.60`.
2. **Fallback Response**:
   * If no document meets the `0.60` similarity threshold, returns:
     *"I don't have enough relevant information in my cybersecurity knowledge base to answer this question reliably."*
3. **Anti-Prompt-Injection Safeguards**:
   * Retrieved document text is treated strictly as untrusted data within the system prompt.
   * System rules explicitly command the model to ignore any instructions embedded inside documents.
4. **Deterministic Scan Explanation (`/ask-scan/{scan_id}`)**:
   * When asked about a specific scan, the numerical TreeSHAP feature contributions and risk level are formatted **deterministically in Python** before being passed to the user. The LLM is not permitted to guess or reinterpret mathematical log-odds scores.

---

## 5. API Endpoints

### 1. General Cybersecurity Inquiry
* **Endpoint**: `POST /api/v1/assistant/ask`
* **Auth**: Bearer JWT (`Authorization: Bearer <token>`)
* **Request Body**:
  ```json
  {
    "question": "What should I do if I entered my password on a suspicious site?",
    "top_k": 3
  }
  ```
* **Response Body**:
  ```json
  {
    "question": "What should I do if I entered my password on a suspicious site?",
    "answer": "Immediately change your password from a secure device...",
    "sources": [
      {
        "source": "phishing_incident_response.md",
        "title": "Phishing Incident Response",
        "source_urls": [],
        "similarity": 0.8124
      }
    ]
  }
  ```

### 2. Scan-Specific Inquiry
* **Endpoint**: `POST /api/v1/assistant/ask-scan/{scan_id}`
* **Auth**: Bearer JWT (Strict user ownership check enforced)
* **Request Body**:
  ```json
  {
    "question": "Why was this URL flagged as phishing?",
    "top_k": 3
  }
  ```
* **Response Body**:
  ```json
  {
    "question": "Why was this URL flagged as phishing?",
    "answer": "SCAN SUMMARY\nURL: https://...\nVerdict: phishing\n...",
    "sources": []
  }
  ```

---

## 6. Offline Ollama & Error Handling

* If the local Ollama daemon is stopped or times out, the API gracefully catches `requests.ConnectionError` and `requests.Timeout` and responds with:
  ```json
  {
    "success": false,
    "error": {
      "code": "HTTP_503",
      "message": "Cybersecurity assistant service is unavailable."
    }
  }
  ```
* Database and scan access violations return `404 Not Found` or `422 Unprocessable Entity` according to the centralized error response standard.
