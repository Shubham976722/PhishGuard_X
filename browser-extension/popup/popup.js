/**
 * PhishGuard X — Popup Script
 * Orchestrates UI states, active tab detection, scan rendering, and settings interaction.
 */

document.addEventListener("DOMContentLoaded", async () => {
  // UI Elements - Views
  const mainView = document.getElementById("mainView");
  const settingsView = document.getElementById("settingsView");

  // UI Elements - Navigation
  const settingsBtn = document.getElementById("settingsBtn");
  const backBtn = document.getElementById("backBtn");
  const rescanBtn = document.getElementById("rescanBtn");
  const retryBtn = document.getElementById("retryBtn");

  // UI Elements - States
  const targetUrlEl = document.getElementById("targetUrl");
  const loadingState = document.getElementById("loadingState");
  const resultState = document.getElementById("resultState");
  const unsupportedState = document.getElementById("unsupportedState");
  const errorState = document.getElementById("errorState");

  // UI Elements - Result Data
  const verdictBadge = document.getElementById("verdictBadge");
  const verdictIcon = document.getElementById("verdictIcon");
  const verdictTitle = document.getElementById("verdictTitle");
  const riskLevelBadge = document.getElementById("riskLevelBadge");
  const scoreValue = document.getElementById("scoreValue");
  const scoreBar = document.getElementById("scoreBar");
  const threatSection = document.getElementById("threatSection");
  const matchTypeVal = document.getElementById("matchTypeVal");
  const threatSourcesVal = document.getElementById("threatSourcesVal");
  const explanationText = document.getElementById("explanationText");
  const unsupportedMsg = document.getElementById("unsupportedMsg");
  const errorTitle = document.getElementById("errorTitle");
  const errorMsg = document.getElementById("errorMsg");
  const backendStatusDot = document.getElementById("backendStatusDot");

  // UI Elements - Settings
  const loggedInState = document.getElementById("loggedInState");
  const userEmailText = document.getElementById("userEmailText");
  const loginForm = document.getElementById("loginForm");
  const loginEmail = document.getElementById("loginEmail");
  const loginPassword = document.getElementById("loginPassword");
  const loginError = document.getElementById("loginError");
  const logoutBtn = document.getElementById("logoutBtn");
  const apiUrlInput = document.getElementById("apiUrlInput");
  const saveApiBtn = document.getElementById("saveApiBtn");
  const saveApiSuccess = document.getElementById("saveApiSuccess");

  let currentTab = null;

  /**
   * Hide all state panels
   */
  function hideAllStates() {
    loadingState.classList.add("hidden");
    resultState.classList.add("hidden");
    unsupportedState.classList.add("hidden");
    errorState.classList.add("hidden");
  }

  /**
   * Switch between Main Scanner and Settings View
   */
  function showView(view) {
    if (view === "settings") {
      mainView.classList.add("hidden");
      settingsView.classList.remove("hidden");
      loadSettingsData();
    } else {
      settingsView.classList.add("hidden");
      mainView.classList.remove("hidden");
    }
  }

  /**
   * Load stored authentication and configuration state
   */
  async function loadSettingsData() {
    chrome.runtime.sendMessage({ action: "GET_CONFIG" }, (config) => {
      if (!config) return;
      apiUrlInput.value = config.apiBaseUrl || "http://127.0.0.1:8000";

      if (config.authToken && config.userEmail) {
        loggedInState.classList.remove("hidden");
        loginForm.classList.add("hidden");
        userEmailText.textContent = config.userEmail;
      } else {
        loggedInState.classList.add("hidden");
        loginForm.classList.remove("hidden");
      }
    });
  }

  /**
   * Render scan result into the popup UI
   */
  function renderScanResult(data) {
    hideAllStates();

    if (data.status === "unsupported") {
      unsupportedState.classList.remove("hidden");
      unsupportedMsg.textContent = data.message || "This URL type cannot be scanned.";
      backendStatusDot.className = "status-dot online";
      return;
    }

    if (data.status === "offline" || data.status === "error" || data.status === "auth_required") {
      errorState.classList.remove("hidden");
      backendStatusDot.className = "status-dot offline";
      errorTitle.textContent = data.status === "auth_required" ? "Authentication Required" : "Scan Error";
      errorMsg.textContent = data.error || "An unexpected error occurred.";
      return;
    }

    backendStatusDot.className = "status-dot online";
    resultState.classList.remove("hidden");

    // Verdict styling
    const verdict = (data.verdict || "unknown").toLowerCase();
    const riskLevel = (data.risk_level || "low").toLowerCase();
    const score = Number(data.risk_score || 0);

    verdictBadge.className = `verdict-banner ${verdict}`;
    riskLevelBadge.className = `risk-badge ${riskLevel}`;
    riskLevelBadge.textContent = `${riskLevel} risk`;

    if (verdict === "legitimate") {
      verdictIcon.textContent = "🛡️";
      verdictTitle.textContent = "Legitimate Website";
    } else if (verdict === "suspicious") {
      verdictIcon.textContent = "⚠️";
      verdictTitle.textContent = "Suspicious Website";
    } else {
      verdictIcon.textContent = "🚨";
      verdictTitle.textContent = "Phishing / Malware Threat";
    }

    // Score bar
    scoreValue.textContent = `${score.toFixed(1)}%`;
    scoreBar.style.width = `${Math.min(Math.max(score, 5), 100)}%`;
    scoreBar.className = `score-fill ${riskLevel}`;

    // Threat intelligence section
    if (data.match_type || (data.threat_sources && data.threat_sources.length > 0)) {
      threatSection.classList.remove("hidden");
      matchTypeVal.textContent = data.match_type === "exact_url" ? "Exact URL Match" : "Hostname Domain Match";
      threatSourcesVal.textContent = data.threat_sources.join(", ") || "External IOC Feed";
    } else {
      threatSection.classList.add("hidden");
    }

    // Explanation
    explanationText.textContent = data.explanation || "No detailed ML feature contributions returned.";
  }

  /**
   * Execute scan for the currently active browser tab
   */
  async function scanCurrentTab(forceRefresh = false) {
    hideAllStates();
    loadingState.classList.remove("hidden");

    if (forceRefresh) {
      await new Promise((res) => chrome.runtime.sendMessage({ action: "CLEAR_CACHE" }, res));
    }

    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (!tabs || tabs.length === 0) {
        hideAllStates();
        unsupportedState.classList.remove("hidden");
        unsupportedMsg.textContent = "No active browser tab detected.";
        return;
      }

      currentTab = tabs[0];
      targetUrlEl.textContent = currentTab.url || "about:blank";
      targetUrlEl.title = currentTab.url || "";

      chrome.runtime.sendMessage(
        { action: "SCAN_URL", url: currentTab.url, tabId: currentTab.id },
        (response) => {
          if (chrome.runtime.lastError) {
            renderScanResult({
              status: "offline",
              error: chrome.runtime.lastError.message || "Failed to communicate with extension background worker.",
            });
            return;
          }
          renderScanResult(response || { status: "error", error: "Empty response from background service worker." });
        }
      );
    });
  }

  // --------------------------------------------------
  // Event Handlers
  // --------------------------------------------------

  settingsBtn.addEventListener("click", () => showView("settings"));
  backBtn.addEventListener("click", () => showView("main"));
  rescanBtn.addEventListener("click", () => scanCurrentTab(true));
  retryBtn.addEventListener("click", () => scanCurrentTab(true));

  saveApiBtn.addEventListener("click", () => {
    const newUrl = apiUrlInput.value.trim();
    if (!newUrl) return;

    chrome.runtime.sendMessage({ action: "SET_CONFIG", apiBaseUrl: newUrl }, () => {
      saveApiSuccess.classList.remove("hidden");
      setTimeout(() => saveApiSuccess.classList.add("hidden"), 2500);
    });
  });

  loginForm.addEventListener("submit", (e) => {
    e.preventDefault();
    loginError.classList.add("hidden");

    const email = loginEmail.value.trim();
    const password = loginPassword.value;

    chrome.runtime.sendMessage({ action: "LOGIN", email, password }, (res) => {
      if (res && res.success) {
        loadSettingsData();
        loginPassword.value = "";
        showView("main");
        scanCurrentTab(true);
      } else {
        loginError.textContent = res?.error || "Login failed.";
        loginError.classList.remove("hidden");
      }
    });
  });

  logoutBtn.addEventListener("click", () => {
    chrome.runtime.sendMessage({ action: "LOGOUT" }, () => {
      loadSettingsData();
    });
  });

  // Initial trigger on popup open
  scanCurrentTab();
});
