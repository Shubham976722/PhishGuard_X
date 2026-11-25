import React, { useEffect, useState } from "react";
import { exportScans, getScanHistory } from "../services/api";
import { filterScansByTimeRange, getScanDisplayMetrics } from "../utils/scanHelpers";
import { DownloadIcon, LockIcon, ReportsIcon } from "./Icons";

export function Reports({ user, onRequireAuth }) {
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState("30d");
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!user) return;
    setLoading(true);
    getScanHistory(100, 0)
      .then((data) => setScans(Array.isArray(data) ? data : []))
      .catch((err) => setError(err.message || "Failed to load audit data."))
      .finally(() => setLoading(false));
  }, [user]);

  if (!user) {
    return (
      <div className="stat-card" style={{ textAlign: "center", padding: "clamp(36px, 6vw, 60px) 20px" }}>
        <div
          style={{
            width: "56px",
            height: "56px",
            borderRadius: "16px",
            background: "#eff6ff",
            color: "var(--color-primary)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            margin: "0 auto 16px",
          }}
        >
          <LockIcon size={28} />
        </div>
        <h2 style={{ fontSize: "20px", fontWeight: 700, marginBottom: "8px" }}>
          Authentication Required
        </h2>
        <p style={{ color: "var(--text-secondary)", maxWidth: "440px", margin: "0 auto 24px", fontSize: "14px" }}>
          Please sign in to generate and download security audit reports and threat intelligence exports.
        </p>
        <button type="button" onClick={onRequireAuth} className="btn-primary" style={{ padding: "10px 24px" }}>
          Sign In to Access Reports
        </button>
      </div>
    );
  }

  const handleDownload = async (format) => {
    setError(null);
    setDownloading(true);
    try {
      await exportScans(format);
    } catch (err) {
      setError(`Failed to download report: ${err.message}`);
    } finally {
      setDownloading(false);
    }
  };

  const rangedScans = filterScansByTimeRange(scans, timeRange);
  const total = rangedScans.length;
  const phishing = rangedScans.filter((s) => getScanDisplayMetrics(s).isPhish).length;
  const safe = rangedScans.filter((s) => getScanDisplayMetrics(s).isSafe).length;
  const unknown = Math.max(0, total - phishing - safe);

  const rangeLabel =
    timeRange === "7d" ? "Last 7 Days" : timeRange === "30d" ? "Last 30 Days" : "All Time";

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px", maxWidth: "900px", margin: "0 auto" }}>
      {/* Header Bar with Date Range & Generate Report (Board 8) */}
      <div className="no-print" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "14px" }}>
        <div>
          <h2 style={{ fontSize: "21px", fontWeight: 800, margin: 0, color: "var(--text-primary)" }}>
            Security Reports
          </h2>
          <span style={{ fontSize: "13px", color: "var(--text-secondary)" }}>
            Generate and export audit summaries ({rangeLabel})
          </span>
        </div>

        <div style={{ display: "flex", gap: "10px", alignItems: "center", flexWrap: "wrap" }}>
          <select
            className="scan-text-input"
            style={{ width: "auto", padding: "8px 14px", fontSize: "13px", cursor: "pointer" }}
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            aria-label="Report time range"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="all">All time</option>
          </select>

          <button
            type="button"
            onClick={() => handleDownload("csv")}
            disabled={downloading}
            className="btn-primary"
            style={{ padding: "8px 18px", fontSize: "13px", minHeight: "40px" }}
          >
            {downloading ? "Generating..." : "Generate Report"}
          </button>
        </div>
      </div>

      {error && <div className="state-card-error" style={{ padding: "16px" }}>{error}</div>}

      {/* Security Summary Report Card (Board 8) */}
      <div className="stat-card report-summary-grid" style={{ padding: "clamp(18px, 4vw, 32px)" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "10px" }}>
            <div
              style={{
                width: "44px",
                height: "44px",
                borderRadius: "12px",
                background: "#eff6ff",
                color: "var(--color-primary)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
              }}
            >
              <ReportsIcon size={22} />
            </div>
            <div>
              <h3 style={{ fontSize: "18px", fontWeight: 800, margin: 0, color: "var(--text-primary)" }}>
                Security Summary Report
              </h3>
              <div style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
                {new Date().toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })} · {rangeLabel}
              </div>
            </div>
          </div>

          <p style={{ fontSize: "14px", color: "var(--text-secondary)", marginBottom: "18px", lineHeight: 1.55 }}>
            A comprehensive overview of your scanned URLs, detected phishing and malware sites, safe classifications, and TreeSHAP risk factors.
          </p>

          {/* Action Buttons matching Board 8 */}
          <div className="report-download-actions no-print" style={{ display: "flex", gap: "10px", marginBottom: "22px", flexWrap: "wrap" }}>
            <button
              type="button"
              onClick={() => window.print()}
              className="btn-primary"
              style={{ padding: "8px 16px", fontSize: "13px" }}
            >
              <DownloadIcon size={15} />
              Download PDF
            </button>
            <button
              type="button"
              onClick={() => handleDownload("csv")}
              disabled={downloading}
              className="filter-pill"
              style={{ padding: "8px 16px", fontSize: "13px" }}
            >
              Export CSV
            </button>
            <button
              type="button"
              onClick={() => handleDownload("json")}
              disabled={downloading}
              className="filter-pill"
              style={{ padding: "8px 16px", fontSize: "13px" }}
            >
              Export JSON
            </button>
          </div>

          <div style={{ borderTop: "1px solid var(--card-border)", paddingTop: "16px" }}>
            <div style={{ fontSize: "11px", fontWeight: 700, textTransform: "uppercase", color: "var(--text-secondary)", letterSpacing: "0.5px", marginBottom: "10px" }}>
              Report Includes:
            </div>
            <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: "8px", fontSize: "13px", color: "var(--text-primary)" }}>
              <li style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{ color: "var(--safe-green)", fontWeight: 800 }}>✓</span>
                <span>Scan Statistics ({loading ? "..." : `${total} Total Scans Analyzed`})</span>
              </li>
              <li style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{ color: "var(--safe-green)", fontWeight: 800 }}>✓</span>
                <span>Threat Detections ({loading ? "..." : `${phishing} Phishing/Malware · ${unknown} Suspicious`})</span>
              </li>
              <li style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{ color: "var(--safe-green)", fontWeight: 800 }}>✓</span>
                <span>Safe Verifications & TreeSHAP Guidance ({loading ? "..." : `${safe} Safe Sites`})</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Document Badge Graphic (Board 8) */}
        <div
          style={{
            background: "linear-gradient(145deg, rgba(37,99,235,0.08) 0%, rgba(99,102,241,0.14) 100%)",
            border: "1px solid #dbeafe",
            borderRadius: "16px",
            height: "190px",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            gap: "10px",
            padding: "16px",
            textAlign: "center",
          }}
        >
          <div
            style={{
              width: "58px",
              height: "70px",
              background: "#ffffff",
              borderRadius: "10px",
              border: "1px solid #bfdbfe",
              boxShadow: "0 8px 18px rgba(37,99,235,0.12)",
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              alignItems: "center",
              gap: "6px",
              padding: "10px",
            }}
          >
            <span style={{ width: "34px", height: "4px", borderRadius: "4px", background: "var(--color-primary)" }} />
            <span style={{ width: "28px", height: "4px", borderRadius: "4px", background: "#93c5fd" }} />
            <span style={{ width: "34px", height: "4px", borderRadius: "4px", background: "#cbd5e1" }} />
            <span style={{ width: "22px", height: "4px", borderRadius: "4px", background: "var(--safe-green)" }} />
          </div>
          <span style={{ fontSize: "11px", fontWeight: 800, letterSpacing: "0.8px", color: "var(--color-primary)" }}>
            VERIFIED AUDIT
          </span>
        </div>
      </div>
    </div>
  );
}
