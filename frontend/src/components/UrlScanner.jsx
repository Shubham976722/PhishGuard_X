import React, { useEffect, useState } from "react";
import { scanUrl, scanPublicUrl } from "../services/api";
import { ScanResult } from "./ScanResult";

const SAMPLE_URLS = [
  { label: "google.com (Safe)", value: "https://www.google.com" },
  { label: "login-secure-update.com", value: "http://login-secure-update.com" },
  { label: "192.168.1.10/bank/verify", value: "http://192.168.1.10/bank/login/verify" },
];

export function UrlScanner({ user, onRequireAuth, onAskAboutScan, initialUrl = "" }) {
  const [url, setUrl] = useState(initialUrl);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (initialUrl) {
      setUrl(initialUrl);
    }
  }, [initialUrl]);

  const executeScan = async (targetUrl) => {
    setError(null);
    const trimmed = (targetUrl ?? url).trim();
    if (!trimmed) {
      setError("Please enter a valid URL to scan.");
      return;
    }

    const formatted =
      !trimmed.startsWith("http://") && !trimmed.startsWith("https://")
        ? `https://${trimmed}`
        : trimmed;

    setLoading(true);
    setResult(null);

    try {
      const scanData = user ? await scanUrl(formatted) : await scanPublicUrl(formatted);
      setResult(scanData);
    } catch (err) {
      setError(err.message || "Please check your internet or backend connection and try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e?.preventDefault();
    executeScan(url);
  };

  return (
    <div className="scanner-container">
      {/* Scanner Input Card (Boards 2 & 3) */}
      <div className="scan-box-wrapper">
        <h2 className="scan-title-center">URL Scanner</h2>
        <p className="scan-subtitle-center">
          Check any link for phishing, suspicious redirects, and known malware threats
        </p>

        <form onSubmit={handleSubmit} className="scan-input-row">
          <input
            type="text"
            className="scan-text-input"
            placeholder="https://example.com/login"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={loading}
            aria-label="URL input"
          />
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? "Scanning..." : "Scan Now"}
          </button>
        </form>

        {/* Quick Sample Test Pills */}
        <div className="hero-quick-samples" style={{ justifyContent: "center", marginTop: "14px" }}>
          <span style={{ fontWeight: 600 }}>Quick test:</span>
          {SAMPLE_URLS.map((sample) => (
            <button
              key={sample.value}
              type="button"
              className="sample-chip-btn"
              disabled={loading}
              onClick={() => {
                setUrl(sample.value);
                executeScan(sample.value);
              }}
            >
              {sample.label}
            </button>
          ))}
        </div>
      </div>

      {/* Loading State (Board 12) */}
      {loading && (
        <div className="state-card-loading">
          <div className="spinner-circle" />
          <h3 style={{ fontSize: "18px", fontWeight: 700, marginBottom: "8px" }}>Scanning URL...</h3>
          <p style={{ fontSize: "14px", color: "var(--text-secondary)", maxWidth: "400px", margin: "0 auto" }}>
            Please wait while we inspect lexical URL signals, TreeSHAP feature contributions, and threat intelligence feeds.
          </p>
        </div>
      )}

      {/* Error State (Board 12) */}
      {error && (
        <div className="state-card-error">
          <div
            style={{
              width: "56px",
              height: "56px",
              background: "var(--danger-bg)",
              border: "2px solid var(--danger-border)",
              borderRadius: "50%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "var(--danger-red)",
              fontSize: "26px",
              fontWeight: 800,
              margin: "0 auto 14px",
            }}
          >
            !
          </div>
          <h3 style={{ fontSize: "18px", fontWeight: 700, color: "var(--danger-red-dark)", marginBottom: "8px" }}>
            Unable to Scan
          </h3>
          <p style={{ fontSize: "14px", color: "var(--text-secondary)", maxWidth: "390px", margin: "0 auto 18px" }}>
            {error}
          </p>
          <button type="button" onClick={handleSubmit} className="btn-primary" style={{ padding: "9px 22px", fontSize: "13px" }}>
            Try Again
          </button>
        </div>
      )}

      {/* Verdict Result Cards (Boards 2 & 3) */}
      {result && (
        <div>
          <ScanResult
            scan={result}
            onAskAboutScan={onAskAboutScan}
            onReset={() => {
              setResult(null);
              setUrl("");
            }}
          />

          {!user && (
            <div
              style={{
                marginTop: "18px",
                padding: "16px 18px",
                background: "#ffffff",
                border: "1px solid var(--card-border)",
                borderRadius: "14px",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                flexWrap: "wrap",
                gap: "12px",
                boxShadow: "var(--card-shadow)",
              }}
            >
              <div style={{ flex: "1 1 240px" }}>
                <div style={{ fontWeight: 700, color: "var(--color-primary)", fontSize: "14px" }}>
                  Guest Scan Completed
                </div>
                <div style={{ fontSize: "13px", color: "var(--text-secondary)", marginTop: "2px" }}>
                  Sign in or register for free to save scan history, view activity charts, and chat with the AI Assistant.
                </div>
              </div>
              <button
                type="button"
                onClick={onRequireAuth}
                className="btn-primary"
                style={{ padding: "9px 18px", fontSize: "13px" }}
              >
                Sign Up / Login
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
