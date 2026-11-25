/**
 * PhishGuard X — Frontend API Client
 * Wraps FastAPI REST endpoints with authentication, token handling, and error transformation.
 */

const API_BASE = "";

function getAuthToken() {
  return localStorage.getItem("phishguard_token");
}

function setAuthToken(token) {
  if (token) {
    localStorage.setItem("phishguard_token", token);
  } else {
    localStorage.removeItem("phishguard_token");
  }
}

async function request(endpoint, options = {}) {
  const token = getAuthToken();
  const headers = {
    "Content-Type": "application/json",
    Accept: "application/json",
    ...(options.headers || {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const errorMsg =
      data.error?.message ||
      data.detail ||
      `Request failed with status ${response.status}`;
    const error = new Error(errorMsg);
    error.status = response.status;
    error.code = data.error?.code;
    error.details = data.error?.details;
    throw error;
  }

  return data;
}

// --------------------------------------------------
// Authentication Endpoints
// --------------------------------------------------

export async function register(fullName, email, password) {
  return request("/api/v1/auth/register", {
    method: "POST",
    body: JSON.stringify({
      full_name: fullName,
      email,
      password,
    }),
  });
}

export async function login(email, password) {
  const result = await request("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });

  if (result.access_token) {
    setAuthToken(result.access_token);
  }

  return result;
}

export function logout() {
  setAuthToken(null);
}

export async function getProfile() {
  return request("/api/v1/auth/me");
}

export function isAuthenticated() {
  return Boolean(getAuthToken());
}

// --------------------------------------------------
// URL Scanning & History Endpoints
// --------------------------------------------------

export async function scanUrl(url) {
  return request("/api/v1/scans/", {
    method: "POST",
    body: JSON.stringify({ url }),
  });
}

export async function scanPublicUrl(url) {
  return request("/api/v1/scans/public", {
    method: "POST",
    body: JSON.stringify({ url }),
  });
}

export async function getScanStats() {
  return request("/api/v1/scans/stats");
}

export async function exportScans(format = "json") {
  const token = getAuthToken();
  const headers = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const response = await fetch(`${API_BASE}/api/v1/scans/export?format=${format}`, {
    headers,
  });

  if (format === "csv") {
    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = downloadUrl;
    a.download = "phishguard_scans.csv";
    document.body.appendChild(a);
    a.click();
    a.remove();
    return true;
  }

  const data = await response.json();
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const downloadUrl = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = downloadUrl;
  a.download = "phishguard_scans.json";
  document.body.appendChild(a);
  a.click();
  a.remove();
  return data;
}

export async function getScanHistory(limit = 20, offset = 0) {
  return request(`/api/v1/scans/history?limit=${limit}&offset=${offset}`);
}

// --------------------------------------------------
// Cybersecurity Assistant Endpoints
// --------------------------------------------------

export async function askAssistant(question, topK = 3) {
  return request("/api/v1/assistant/ask", {
    method: "POST",
    body: JSON.stringify({ question, top_k: topK }),
  });
}

export async function askAboutScan(scanId, question, topK = 3) {
  return request(`/api/v1/assistant/ask-scan/${scanId}`, {
    method: "POST",
    body: JSON.stringify({ question, top_k: topK }),
  });
}

// --------------------------------------------------
// Health Check
// --------------------------------------------------

export async function checkHealth() {
  return request("/api/v1/health/ready");
}
