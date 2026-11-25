/**
 * PhishGuard X — Chrome Extension Background Service Worker (Manifest V3)
 * Handles background scanning, badge updates, caching, and FastAPI backend communication.
 */

const DEFAULT_API_BASE = "http://127.0.0.1:8000";
const CACHE_TTL_MS = 5 * 60 * 1000; // 5 minutes cache

// In-memory cache for recent scans: url -> { result, timestamp }
const scanCache = new Map();

/**
 * Retrieve configuration from chrome.storage.local
 */
async function getConfig() {
  const data = await chrome.storage.local.get(["apiBaseUrl", "authToken", "userEmail"]);
  return {
    apiBaseUrl: data.apiBaseUrl || DEFAULT_API_BASE,
    authToken: data.authToken || null,
    userEmail: data.userEmail || null,
  };
}

/**
 * Verify whether URL is eligible for phishing/threat scanning
 */
function isSupportedUrl(url) {
  if (!url || typeof url !== "string") return false;
  try {
    const parsed = new URL(url);
    return parsed.protocol === "http:" || parsed.protocol === "https:";
  } catch {
    return false;
  }
}

/**
 * Update the extension icon badge to reflect security status
 */
function updateBadge(verdict, tabId) {
  if (!tabId) return;

  switch (verdict) {
    case "legitimate":
      chrome.action.setBadgeText({ text: "SAFE", tabId });
      chrome.action.setBadgeBackgroundColor({ color: "#16a34a", tabId }); // Emerald green
      break;
    case "suspicious":
      chrome.action.setBadgeText({ text: "WARN", tabId });
      chrome.action.setBadgeBackgroundColor({ color: "#d97706", tabId }); // Amber
      break;
    case "phishing":
    case "malware":
      chrome.action.setBadgeText({ text: "ALERT", tabId });
      chrome.action.setBadgeBackgroundColor({ color: "#dc2626", tabId }); // Crimson red
      break;
    default:
      chrome.action.setBadgeText({ text: "", tabId });
      break;
  }
}

/**
 * Perform a URL scan against the PhishGuard X API
 */
async function performScan(targetUrl, tabId) {
  if (!isSupportedUrl(targetUrl)) {
    return {
      status: "unsupported",
      message: "PhishGuard X only scans public HTTP and HTTPS websites.",
      url: targetUrl,
    };
  }

  // Check cache
  const cached = scanCache.get(targetUrl);
  if (cached && (Date.now() - cached.timestamp < CACHE_TTL_MS)) {
    if (tabId) updateBadge(cached.result.verdict, tabId);
    return { ...cached.result, cached: true };
  }

  const config = await getConfig();
  const endpoint = `${config.apiBaseUrl.replace(/\/+$/, "")}/api/v1/scans/`;

  const headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
  };

  if (config.authToken) {
    headers["Authorization"] = `Bearer ${config.authToken}`;
  }

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s timeout

    const response = await fetch(endpoint, {
      method: "POST",
      headers,
      body: JSON.stringify({ url: targetUrl }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    const data = await response.json();

    if (!response.ok) {
      if (response.status === 401) {
        return {
          status: "auth_required",
          error: "Authentication required to scan URLs. Please log in through extension settings.",
        };
      }
      return {
        status: "error",
        error: data.error?.message || `Backend error (HTTP ${response.status})`,
      };
    }

    // Success response
    const result = {
      status: "success",
      id: data.id,
      url: data.url,
      verdict: data.verdict,
      risk_score: data.risk_score,
      risk_level: data.risk_level,
      threat_type: data.threat_type,
      match_type: data.match_type,
      threat_sources: data.threat_sources || [],
      threat_types: data.threat_types || [],
      explanation: data.explanation,
      scanned_at: data.scanned_at,
    };

    scanCache.set(targetUrl, { result, timestamp: Date.now() });

    if (tabId) {
      updateBadge(result.verdict, tabId);
    }

    return result;

  } catch (err) {
    if (err.name === "AbortError") {
      return {
        status: "offline",
        error: "Scan request timed out. Please check if PhishGuard X backend is running.",
      };
    }
    return {
      status: "offline",
      error: "Unable to connect to PhishGuard X backend. Ensure FastAPI server is running on " + config.apiBaseUrl,
    };
  }
}

/**
 * Authenticate user with PhishGuard X credentials
 */
async function authenticateUser(email, password) {
  const config = await getConfig();
  const endpoint = `${config.apiBaseUrl.replace(/\/+$/, "")}/api/v1/auth/login`;

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();

    if (!response.ok) {
      return {
        success: false,
        error: data.error?.message || "Invalid credentials",
      };
    }

    await chrome.storage.local.set({
      authToken: data.access_token,
      userEmail: email,
    });

    return { success: true, email };

  } catch {
    return {
      success: false,
      error: "Unable to connect to authentication server.",
    };
  }
}

// --------------------------------------------------
// Runtime Message Listener
// --------------------------------------------------

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "SCAN_URL") {
    performScan(message.url, message.tabId).then(sendResponse);
    return true; // Keep message channel open for async response
  }

  if (message.action === "LOGIN") {
    authenticateUser(message.email, message.password).then(sendResponse);
    return true;
  }

  if (message.action === "LOGOUT") {
    chrome.storage.local.remove(["authToken", "userEmail"]).then(() => {
      sendResponse({ success: true });
    });
    return true;
  }

  if (message.action === "GET_CONFIG") {
    getConfig().then(sendResponse);
    return true;
  }

  if (message.action === "SET_CONFIG") {
    chrome.storage.local.set({ apiBaseUrl: message.apiBaseUrl }).then(() => {
      sendResponse({ success: true });
    });
    return true;
  }

  if (message.action === "CLEAR_CACHE") {
    scanCache.clear();
    sendResponse({ success: true });
    return true;
  }
});
