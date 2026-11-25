# PhishGuard X — Chrome Manifest V3 Browser Extension

## 1. Overview & Architecture

The **PhishGuard X Browser Extension** provides real-time phishing and malware detection directly inside Chromium-based browsers (Google Chrome, Brave, Microsoft Edge). It connects securely to the PhishGuard X FastAPI backend (`/api/v1/scans/`) to evaluate the active tab's URL using:
1. Lexical and structural URL feature extraction
2. LightGBM TreeSHAP explainable machine learning predictions
3. Real-time Threat Intelligence lookup (Phishing.Database + URLhaus)

---

## 2. Manifest V3 Security & Permissions

The extension strictly follows Google's **Manifest V3** security model and the principle of least privilege:

* **No broad `<all_urls>` permission**: The extension only accesses the current tab's URL when the user clicks the extension action (`activeTab`).
* **Storage permission (`storage`)**: Stores the user's JWT access token, customized backend API URL, and a 5-minute in-memory cache to prevent redundant scan requests.
* **No Hardcoded Secrets**: Extension code contains zero embedded API keys, JWT secrets, or database URLs. Authentication is handled dynamically through the `/api/v1/auth/login` endpoint.

---

## 3. Directory Structure

```
browser-extension/
├── manifest.json              # Manifest V3 specification
├── background/
│   └── service_worker.js      # Background service worker, badge updater & cache
├── popup/
│   ├── popup.html             # Scanner popup & settings drawer markup
│   ├── popup.css              # Cyber-defense UI styling & verdict banners
│   └── popup.js               # Tab detection, scan orchestration & auth state
└── icons/
    ├── icon16.png             # 16x16 badge icon
    ├── icon48.png             # 48x48 toolbar icon
    ├── icon128.png            # 128x128 store/management icon
    └── icon.svg               # Vector master logo
```

---

## 4. How to Install & Load in Chrome

1. Open Google Chrome (or any Chromium browser).
2. Navigate to `chrome://extensions/`.
3. Enable **Developer mode** toggle in the top-right corner.
4. Click **Load unpacked** in the top-left corner.
5. Select the folder:
   `C:\Users\shubh\Desktop\PhishGuard_X\browser-extension`
6. The PhishGuard X shield icon will appear in your browser toolbar. Pin it for quick access.

---

## 5. Key Features

### Real-Time Verdict States
* **Legitimate (Safe)**: Green banner, low risk score ($<10\%$), green `SAFE` toolbar badge.
* **Suspicious (Caution)**: Amber banner, medium risk score ($10\% - 50\%$) or hostname threat match, amber `WARN` toolbar badge.
* **Phishing / Malware (Danger)**: Crimson banner, high risk score ($>50\%$) or exact URL threat match, red `ALERT` toolbar badge.
* **Internal / Unsupported Pages**: Graceful handling for `chrome://`, `about:blank`, `file://` with informative guidance.

### Explanation & Threat Evidence
* Displays risk score percentage.
* Reveals threat intelligence feed matches (`Phishing.Database`, `URLhaus`) with match type (Exact URL vs Hostname).
* Shows the top contributing features that influenced the AI prediction.

### Settings & User Account
* Click the Settings gear icon in the popup header to:
  * Configure custom backend URL (default: `http://127.0.0.1:8000`).
  * Log in with PhishGuard X credentials to sync scans to your account history.
  * Log out safely.
