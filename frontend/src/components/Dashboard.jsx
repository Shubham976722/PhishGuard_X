import React, { useEffect, useState } from "react";
import { getScanHistory, getScanStats } from "../services/api";
import {
  buildWeeklyActivitySeries,
  formatScanDate,
  getScanDisplayMetrics,
} from "../utils/scanHelpers";
import {
  LightbulbIcon,
  LockIcon,
  ScannerIcon,
  ShieldAlertBadgeIcon,
  ShieldCheckBadgeIcon,
  SparklesIcon,
} from "./Icons";

function buildSmoothPath(points) {
  if (!points.length) return "";
  if (points.length === 1) return `M ${points[0].x} ${points[0].y}`;
  let d = `M ${points[0].x} ${points[0].y}`;
  for (let i = 0; i < points.length - 1; i++) {
    const curr = points[i];
    const next = points[i + 1];
    const midX = (curr.x + next.x) / 2;
    d += ` C ${midX} ${curr.y}, ${midX} ${next.y}, ${next.x} ${next.y}`;
  }
  return d;
}

export function Dashboard({ user, onRequireAuth, onNavigateTab, onSelectScan }) {
  const [stats, setStats] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [hoveredIdx, setHoveredIdx] = useState(null);

  useEffect(() => {
    if (!user) return;
    let active = true;
    setLoading(true);
    setError(null);

    Promise.all([getScanStats(), getScanHistory(100, 0).catch(() => [])])
      .then(([statsData, historyData]) => {
        if (!active) return;
        setStats(statsData);
        setHistory(Array.isArray(historyData) ? historyData : []);
      })
      .catch((err) => {
        if (!active) return;
        setError(err.message || "Failed to load dashboard telemetry.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
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
          Please sign in to view your personal security overview, activity timeline, and recent threat detections.
        </p>
        <button type="button" onClick={onRequireAuth} className="btn-primary" style={{ padding: "10px 24px" }}>
          Sign In to Access Dashboard
        </button>
      </div>
    );
  }

  const total = stats?.total_scans ?? 0;
  const phishing = stats?.phishing_scans ?? 0;
  const safe = stats?.legitimate_scans ?? 0;
  const unknown = stats?.suspicious_scans ?? 0;
  const activeIndicators = stats?.active_threat_indicators ?? 0;
  const recentScans = (stats?.recent_scans?.length ? stats.recent_scans : history.slice(0, 5)) || [];

  // Build dynamic 7-day SVG coordinates
  const series = buildWeeklyActivitySeries(history);
  const maxDailyCount = Math.max(4, ...series.map((d) => Math.max(d.safe, d.phishing, d.unknown)));
  const chartLeft = 42;
  const chartRight = 668;
  const chartTop = 24;
  const chartBottom = 148;
  const stepX = series.length > 1 ? (chartRight - chartLeft) / (series.length - 1) : 0;

  const toPoints = (key) =>
    series.map((day, idx) => ({
      x: Math.round(chartLeft + idx * stepX),
      y: Math.round(chartBottom - (day[key] / maxDailyCount) * (chartBottom - chartTop)),
    }));

  const safePoints = toPoints("safe");
  const phishPoints = toPoints("phishing");
  const unknownPoints = toPoints("unknown");

  const safePath = buildSmoothPath(safePoints);
  const phishPath = buildSmoothPath(phishPoints);
  const unknownPath = buildSmoothPath(unknownPoints);
  const safeAreaPath = safePoints.length
    ? `${safePath} L ${safePoints[safePoints.length - 1].x} ${chartBottom} L ${safePoints[0].x} ${chartBottom} Z`
    : "";

  const activeHoverDay = hoveredIdx != null ? series[hoveredIdx] : null;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      {error && (
        <div className="state-card-error" style={{ padding: "14px 18px", textAlign: "left", fontSize: "13px" }}>
          {error}
        </div>
      )}

      {/* 4 Stat Cards (Board 4) */}
      <div className="stat-card-grid" style={{ marginBottom: 0 }}>
        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Total Scans</span>
            <div className="stat-icon-wrap" style={{ background: "rgba(37, 99, 235, 0.1)", color: "var(--color-primary)" }}>
              <ScannerIcon size={18} />
            </div>
          </div>
          <div className="stat-value">{loading ? "—" : total}</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Phishing Detections</span>
            <div className="stat-icon-wrap" style={{ background: "var(--danger-bg)", color: "var(--danger-red)" }}>
              <ShieldAlertBadgeIcon size={18} />
            </div>
          </div>
          <div className="stat-value" style={{ color: "var(--danger-red)" }}>
            {loading ? "—" : phishing}
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Safe Sites</span>
            <div className="stat-icon-wrap" style={{ background: "var(--safe-bg)", color: "var(--safe-green)" }}>
              <ShieldCheckBadgeIcon size={18} />
            </div>
          </div>
          <div className="stat-value" style={{ color: "var(--safe-green)" }}>
            {loading ? "—" : safe}
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">Unknown</span>
            <div className="stat-icon-wrap" style={{ background: "var(--amber-bg)", color: "var(--amber-warn-dark)" }}>
              <SparklesIcon size={18} />
            </div>
          </div>
          <div className="stat-value" style={{ color: "var(--amber-warn-dark)" }}>
            {loading ? "—" : unknown}
          </div>
        </div>
      </div>

      {/* Interactive Scan Activity Chart (Board 4) */}
      <div className="stat-card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px", marginBottom: "14px" }}>
          <div>
            <h3 style={{ fontSize: "16px", fontWeight: 700, margin: 0 }}>Scan Activity</h3>
            <span style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
              Last 7 days inspection telemetry
            </span>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "14px", flexWrap: "wrap" }}>
            <div style={{ display: "flex", gap: "12px", fontSize: "12px", flexWrap: "wrap" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "var(--safe-green)" }} />
                <span style={{ color: "var(--text-secondary)" }}>Safe</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "var(--danger-red)" }} />
                <span style={{ color: "var(--text-secondary)" }}>Phishing</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "var(--amber-warn)" }} />
                <span style={{ color: "var(--text-secondary)" }}>Unknown</span>
              </div>
            </div>

            {onNavigateTab && (
              <button
                type="button"
                className="btn-primary"
                style={{ padding: "7px 14px", fontSize: "12px" }}
                onClick={() => onNavigateTab("scanner")}
              >
                + New Scan
              </button>
            )}
          </div>
        </div>

        {/* Hover Summary Strip */}
        <div
          style={{
            minHeight: "28px",
            marginBottom: "6px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: "8px",
            fontSize: "12px",
            color: "var(--text-secondary)",
          }}
        >
          {activeHoverDay ? (
            <span style={{ background: "#f1f5f9", padding: "4px 10px", borderRadius: "9999px", fontWeight: 600, color: "var(--text-primary)" }}>
              {activeHoverDay.label}: {activeHoverDay.safe} Safe · {activeHoverDay.phishing} Phishing · {activeHoverDay.unknown} Unknown
            </span>
          ) : (
            <span>Hover or tap a day column to inspect exact daily breakdown</span>
          )}
        </div>

        <div style={{ width: "100%", height: "190px", position: "relative" }}>
          <svg viewBox="0 0 700 185" preserveAspectRatio="none" style={{ width: "100%", height: "100%" }}>
            <defs>
              <linearGradient id="pgSafeAreaGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#10b981" stopOpacity="0.22" />
                <stop offset="100%" stopColor="#10b981" stopOpacity="0.0" />
              </linearGradient>
            </defs>

            {/* Horizontal Grid Lines & Y Labels */}
            {[0, 0.5, 1].map((ratio) => {
              const y = Math.round(chartBottom - ratio * (chartBottom - chartTop));
              const tickVal = Math.round(ratio * maxDailyCount);
              return (
                <g key={ratio}>
                  <line x1={chartLeft} y1={y} x2={chartRight} y2={y} stroke="#f1f5f9" strokeWidth="1.2" />
                  <text x="12" y={y + 4} fill="#94a3b8" fontSize="11">
                    {tickVal}
                  </text>
                </g>
              );
            })}

            {/* Area & Trend Curves */}
            {safeAreaPath && <path d={safeAreaPath} fill="url(#pgSafeAreaGrad)" />}
            {safePath && <path d={safePath} fill="none" stroke="#10b981" strokeWidth="2.6" strokeLinecap="round" />}
            {phishPath && <path d={phishPath} fill="none" stroke="#ef4444" strokeWidth="2.6" strokeLinecap="round" />}
            {unknownPath && (
              <path d={unknownPath} fill="none" stroke="#f59e0b" strokeWidth="2" strokeDasharray="4 4" strokeLinecap="round" />
            )}

            {/* Data Dots + Interactive Column Targets */}
            {series.map((day, idx) => {
              const x = safePoints[idx].x;
              const isSelected = hoveredIdx === idx;
              return (
                <g
                  key={day.key}
                  style={{ cursor: "pointer" }}
                  onMouseEnter={() => setHoveredIdx(idx)}
                  onClick={() => setHoveredIdx(idx)}
                >
                  {isSelected && (
                    <line x1={x} y1={chartTop} x2={x} y2={chartBottom} stroke="#cbd5e1" strokeWidth="1.5" strokeDasharray="3 3" />
                  )}
                  <circle cx={safePoints[idx].x} cy={safePoints[idx].y} r={isSelected ? 5 : 3.5} fill="#10b981" stroke="#ffffff" strokeWidth="1.5" />
                  <circle cx={phishPoints[idx].x} cy={phishPoints[idx].y} r={isSelected ? 5 : 3.5} fill="#ef4444" stroke="#ffffff" strokeWidth="1.5" />
                  <circle cx={unknownPoints[idx].x} cy={unknownPoints[idx].y} r={isSelected ? 4.5 : 3} fill="#f59e0b" stroke="#ffffff" strokeWidth="1.5" />
                  <text
                    x={x}
                    y="174"
                    textAnchor="middle"
                    fill={isSelected ? "#0f172a" : "#94a3b8"}
                    fontWeight={isSelected ? "700" : "500"}
                    fontSize="11"
                  >
                    {day.label}
                  </text>
                  <rect x={x - 35} y={chartTop} width="70" height={chartBottom - chartTop + 28} fill="transparent" />
                </g>
              );
            })}
          </svg>
        </div>
      </div>

      {/* Bottom 2-Column Area: Recent Scans + Security Tips & Threat Feed Health */}
      <div className="dashboard-bottom-grid">
        <div className="stat-card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px", gap: "8px" }}>
            <h3 style={{ fontSize: "15px", fontWeight: 700, margin: 0 }}>Recent Scans</h3>
            {onNavigateTab && (
              <button
                type="button"
                onClick={() => onNavigateTab("history")}
                style={{ background: "none", border: "none", color: "var(--color-primary)", fontSize: "12px", fontWeight: 600, cursor: "pointer" }}
              >
                View All →
              </button>
            )}
          </div>

          {recentScans.length === 0 ? (
            <div style={{ padding: "20px 0", textAlign: "center", color: "var(--text-secondary)", fontSize: "13px" }}>
              No URL scans recorded yet. Start by scanning any link to populate your security telemetry.
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              {recentScans.map((scan) => {
                const { statusKey, statusLabel, confidence } = getScanDisplayMetrics(scan);
                const pillClass =
                  statusKey === "safe"
                    ? "badge-pill-safe"
                    : statusKey === "danger"
                      ? "badge-pill-danger"
                      : "badge-pill-warn";

                return (
                  <div
                    key={scan.id}
                    onClick={() => onSelectScan && onSelectScan(scan)}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      gap: "12px",
                      padding: "10px 12px",
                      borderRadius: "10px",
                      border: "1px solid var(--card-border)",
                      background: "#f8fafc",
                      cursor: onSelectScan ? "pointer" : "default",
                    }}
                  >
                    <div style={{ minWidth: 0, flex: 1 }}>
                      <div style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-primary)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {scan.url}
                      </div>
                      <div style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "2px" }}>
                        {formatScanDate(scan.scanned_at)} · Confidence {confidence}%
                      </div>
                    </div>
                    <span className={pillClass} style={{ fontSize: "11px" }}>
                      {statusLabel}
                    </span>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {/* Security Tips Card (Board 4) */}
          <div className="stat-card" style={{ gap: "12px" }}>
            <div style={{ display: "flex", alignItems: "flex-start", gap: "12px" }}>
              <div
                style={{
                  width: "38px",
                  height: "38px",
                  background: "var(--amber-bg)",
                  color: "var(--amber-warn-dark)",
                  border: "1px solid var(--amber-border)",
                  borderRadius: "10px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  flexShrink: 0,
                }}
              >
                <LightbulbIcon size={20} />
              </div>
              <div>
                <div style={{ fontSize: "14px", fontWeight: 700, color: "var(--text-primary)" }}>
                  Security Tips
                </div>
                <p style={{ fontSize: "13px", color: "var(--text-secondary)", marginTop: "4px", lineHeight: 1.55 }}>
                  Always check links before clicking, especially from urgent messages. Watch for raw IP hosts, brand lookalike hyphens, and insecure HTTP login forms.
                </p>
              </div>
            </div>
          </div>

          {/* Threat Feed Sync Summary */}
          <div className="stat-card" style={{ background: "linear-gradient(135deg, #eff6ff 0%, #f5f3ff 100%)", borderColor: "#dbeafe" }}>
            <div style={{ fontSize: "12px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.6px", color: "var(--color-primary)" }}>
              Threat Feed Engine
            </div>
            <div style={{ fontSize: "24px", fontWeight: 800, color: "var(--text-primary)", marginTop: "6px" }}>
              {activeIndicators > 0 ? activeIndicators.toLocaleString() : "Active"}
            </div>
            <div style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "4px" }}>
              {activeIndicators > 0
                ? "Verified active phishing & malware threat indicators indexed."
                : "Local ML classification & threat intel lookup engine ready."}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
