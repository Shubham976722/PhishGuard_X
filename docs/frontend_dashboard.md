# PhishGuard X — React / Vite Web Dashboard

## 1. Overview & Architecture

The **PhishGuard X Frontend Dashboard** is a responsive single-page web application built with **React 18** and **Vite**. It provides users with a complete interface for:
* Interactive URL Scanning with real-time AI & Threat Intelligence verdict displays.
* TreeSHAP feature explainability inspection.
* Historical scan audit log with pagination and detailed drill-downs.
* Private, context-grounded AI Cybersecurity Assistant chat.
* User account registration, login, and JWT session handling.

---

## 2. Directory Structure

```
frontend/
├── package.json              # Project scripts & React dependencies
├── vite.config.js            # Vite build configuration & /api reverse proxy
├── index.html                # Entry HTML shell with Google Fonts
├── public/
│   └── icons/
│       └── icon.svg          # Master vector branding icon
├── src/
│   ├── main.jsx              # React DOM mounting
│   ├── App.jsx               # Main application controller & state
│   ├── index.css             # Cyber-defense UI stylesheet
│   ├── services/
│   │   └── api.js            # FastAPI HTTP client with JWT handling
│   └── components/
│       ├── Navbar.jsx        # Navigation & auth status bar
│       ├── UrlScanner.jsx    # Real-time scan form & radar animation
│       ├── ScanResult.jsx    # Verdict banner, risk gauge & TreeSHAP breakdown
│       ├── ScanHistory.jsx   # Tabular audit trail of previous scans
│       ├── AssistantChat.jsx # Interactive RAG assistant chat
│       └── AuthModal.jsx     # Registration & sign-in modal
└── dist/                     # Optimized production bundle
    ├── index.html
    └── assets/
        ├── index-*.js
        └── index-*.css
```

---

## 3. How to Run the Dashboard

### Development Server
To launch the Vite development server with hot module reloading (HMR) and automatic API proxying to `http://127.0.0.1:8000`:
```powershell
cd frontend
npm run dev
```
The application will be accessible at: `http://localhost:3000`

### Production Build & Preview
To build and preview the optimized production distribution:
```powershell
cd frontend
npm run build
npm run preview
```
Production assets are generated in `frontend/dist/`.

---

## 4. Key Workflows & API Integration

### 1. Live URL Inspection
* User enters a URL starting with `http://` or `https://`.
* Form dispatches `POST /api/v1/scans/`.
* Displays:
  * Security Verdict: **Legitimate** (Green), **Suspicious** (Amber), or **Threat** (Crimson).
  * Phishing Probability Gauge ($0\% - 100\%$).
  * Threat Intelligence match type and active source lists (`Phishing.Database`, `URLhaus`).
  * Top contributing features from TreeSHAP log-odds explanations.
  * Quick-action button: *"Ask AI Assistant About This Scan"*.

### 2. Historical Audit Trail
* Connects to `GET /api/v1/scans/history`.
* Scoped strictly to the authenticated user's records.
* Clicking any historical scan row focuses the view and allows targeted inquiry with the RAG assistant.

### 3. AI Cybersecurity Assistant Chat
* General queries dispatch to `POST /api/v1/assistant/ask`.
* Scan-specific inquiries dispatch to `POST /api/v1/assistant/ask-scan/{id}` with deterministic feature breakdowns.
* Predefined prompt chips provide quick guidance on common phishing topics.
