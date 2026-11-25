import React, { useState } from "react";
import {
  formatScanDate,
  getScanDisplayMetrics,
  parseScanExplanation,
} from "../utils/scanHelpers";
import {
  AssistantIcon,
  DownloadIcon,
  ShieldAlertBadgeIcon,
  ShieldCheckBadgeIcon,
} from "./Icons";

export function ScanDetails({ scan, onBack, onAskAboutScan }) {
  const [activeSubTab, setActiveSubTab] = useState("overview");

  if (!scan) return null;

  const { isSafe, isPhish, statusKey, statusLabel, confidence } = getScanDisplayMetrics(scan);
  const parsed = parseScanExplanation(scan.explanation);
  const hasThreatMatches = Array.isArray(scan.threat_sources) && scan.threat_sources.length > 0;

  const maxAbsContribution = Math.max(
    0.1,
    ...parsed.factors.map((f) => Math.abs(f.contribution))
  );

  const handleDownload = () => {
    const blob = new Blob([JSON.stringify(scan, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `scan_${scan.id || "detail"}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  const bannerStyle =
    statusKey === "safe"
      ? { bg: "var(--safe-bg)", border: "var(--safe-border)", badgeBg: "var(--safe-green)", text: "var(--safe-green-dark)" }
      : statusKey === "danger"
        ? { bg: "var(--danger-bg)", border: "var(--danger-border)", badgeBg: "var(--danger-red)", text: "var(--danger-red-dark)" }
        : { bg: "var(--amber-bg)", border: "var(--amber-border)", badgeBg: "var(--amber-warn)", text: "var(--amber-warn-dark)" };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "18px", maxWidth: "900px", margin: "0 auto" }}>
      {/* Top Action Bar (Board 6) */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "10px" }}>
        <button
          type="button"
          onClick={onBack}
          style={{
            background: "#ffffff",
            border: "1px solid var(--card-border)",
            borderRadius: "9px",
            padding: "8px 14px",
            color: "var(--text-primary)",
            fontSize: "13px",
            fontWeight: 600,
            cursor: "pointer",
            display: "inline-flex",
            alignItems: "center",
            gap: "6px",
            minHeight: "40px",
          }}
        >
          ← Back to History
        </button>

        <button
          type="button"
          onClick={handleDownload}
          className="btn-primary"
          style={{ padding: "8px 18px", fontSize: "13px", minHeight: "40px" }}
        >
          <DownloadIcon size={15} />
          Download Report
        </button>
      </div>

      {/* Main Inspection Card */}
      <div className="stat-card" style={{ padding: "clamp(16px, 3.5vw, 28px)" }}>
        <div style={{ marginBottom: "16px" }}>
          <h2
            style={{
              fontSize: "clamp(17px, 3vw, 21px)",
              fontWeight: 800,
              color: "var(--text-primary)",
              wordBreak: "break-all",
              fontFamily: "var(--font-mono)",
            }}
          >
            {scan.url}
          </h2>
          <div style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "4px" }}>
            Scanned on {formatScanDate(scan.scanned_at, true)}
          </div>
        </div>

        {/* Verdict Banner (Board 6) */}
        <div
          style={{
            background: bannerStyle.bg,
            border: `1px solid ${bannerStyle.border}`,
            borderRadius: "12px",
            padding: "14px 18px",
            display: "flex",
            alignItems: "center",
            gap: "14px",
            marginBottom: "22px",
            flexWrap: "wrap",
          }}
        >
          <div
            style={{
              width: "42px",
              height: "42px",
              borderRadius: "50%",
              background: bannerStyle.badgeBg,
              color: "#ffffff",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flexShrink: 0,
            }}
          >
            {isSafe ? <ShieldCheckBadgeIcon size={22} /> : <ShieldAlertBadgeIcon size={22} />}
          </div>
          <div>
            <div style={{ fontSize: "16px", fontWeight: 800, color: bannerStyle.text }}>
              {isSafe ? "Safe Website" : isPhish ? "Phishing Website" : "Suspicious Website"}
            </div>
            <div style={{ fontSize: "13px", color: bannerStyle.text, opacity: 0.9 }}>
              Risk level: {scan.risk_level || statusLabel} · Confidence: {confidence}%
            </div>
          </div>
        </div>

        {/* Underline Sub-Tabs matching Board 6 */}
        <div
          style={{
            display: "flex",
            gap: "6px",
            borderBottom: "2px solid #e2e8f0",
            marginBottom: "20px",
            overflowX: "auto",
            WebkitOverflowScrolling: "touch",
          }}
          role="tablist"
        >
          {[
            { id: "overview", label: "Overview" },
            { id: "threat-intel", label: "Threat Intelligence" },
            { id: "ai-explanation", label: "AI Explanation" },
          ].map((tab) => {
            const isTabActive = activeSubTab === tab.id;
            return (
              <button
                key={tab.id}
                type="button"
                role="tab"
                aria-selected={isTabActive}
                onClick={() => setActiveSubTab(tab.id)}
                style={{
                  background: "transparent",
                  color: isTabActive ? "var(--color-primary)" : "var(--text-secondary)",
                  border: "none",
                  borderBottom: isTabActive ? "2px solid var(--color-primary)" : "2px solid transparent",
                  marginBottom: "-2px",
                  padding: "10px 16px",
                  fontSize: "13px",
                  fontWeight: isTabActive ? 700 : 600,
                  cursor: "pointer",
                  whiteSpace: "nowrap",
                }}
              >
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Tab 1: Overview (2-Column Grid matching Board 6) */}
        {activeSubTab === "overview" && (
          <div className="grid-2-col" style={{ marginBottom: "22px" }}>
            <div style={{ background: "#f8fafc", border: "1px solid var(--card-border)", borderRadius: "12px", padding: "18px" }}>
              <div style={{ fontSize: "11px", textTransform: "uppercase", color: "var(--text-secondary)", fontWeight: 700, letterSpacing: "0.5px", marginBottom: "8px" }}>
                ML Prediction
              </div>
              <div style={{ fontSize: "17px", fontWeight: 800, color: bannerStyle.badgeBg, marginBottom: "14px" }}>
                {statusLabel}
              </div>

              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px", marginBottom: "8px" }}>
                <span style={{ color: "var(--text-secondary)" }}>Model Engine:</span>
                <span style={{ fontWeight: 600 }}>{parsed.modelName}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px", marginBottom: "8px" }}>
                <span style={{ color: "var(--text-secondary)" }}>Phishing Probability:</span>
                <span style={{ fontWeight: 600 }}>{parsed.probabilityText || `${confidence}%`}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px" }}>
                <span style={{ color: "var(--text-secondary)" }}>Assigned Risk Level:</span>
                <span style={{ fontWeight: 600, textTransform: "capitalize" }}>{scan.risk_level || "Standard"}</span>
              </div>
            </div>

            <div style={{ background: "#f8fafc", border: "1px solid var(--card-border)", borderRadius: "12px", padding: "18px" }}>
              <div style={{ fontSize: "11px", textTransform: "uppercase", color: "var(--text-secondary)", fontWeight: 700, letterSpacing: "0.5px", marginBottom: "8px" }}>
                Threat Intelligence
              </div>
              <div style={{ fontSize: "14px", fontWeight: 700, color: "var(--text-primary)", marginBottom: "12px" }}>
                {hasThreatMatches ? `Found in ${scan.threat_sources.join(", ")}` : "No Active Blocklist Matches"}
              </div>

              <div style={{ fontSize: "12px", color: "var(--text-secondary)", fontWeight: 700, marginBottom: "6px" }}>
                Key Features:
              </div>
              <ul style={{ margin: 0, paddingLeft: "16px", fontSize: "12px", color: "var(--text-secondary)", lineHeight: 1.65 }}>
                {parsed.factors.length > 0 ? (
                  parsed.factors.slice(0, 3).map((f) => (
                    <li key={f.feature}>
                      <strong>{f.feature}:</strong> {f.impactText}
                    </li>
                  ))
                ) : (
                  <>
                    <li>{isSafe ? "Standard canonical domain structure" : "Suspicious lexical URL characteristics"}</li>
                    <li>{isSafe ? "Low risk probability score" : "Elevated risk prediction"}</li>
                  </>
                )}
              </ul>
            </div>
          </div>
        )}

        {/* Tab 2: Threat Intelligence */}
        {activeSubTab === "threat-intel" && (
          <div style={{ background: "#f8fafc", border: "1px solid var(--card-border)", borderRadius: "12px", padding: "18px", marginBottom: "22px" }}>
            <h4 style={{ fontSize: "14px", fontWeight: 700, marginBottom: "12px" }}>Threat Feed Attribution</h4>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "12px", fontSize: "13px" }}>
              <div>
                <div style={{ color: "var(--text-muted)", fontSize: "11px", fontWeight: 700 }}>MATCHED SOURCES</div>
                <div style={{ fontWeight: 600, marginTop: "2px" }}>
                  {hasThreatMatches ? scan.threat_sources.join(", ") : "None (Clean)"}
                </div>
              </div>
              <div>
                <div style={{ color: "var(--text-muted)", fontSize: "11px", fontWeight: 700 }}>MATCH TYPE</div>
                <div style={{ fontWeight: 600, marginTop: "2px" }}>{scan.match_type || "None"}</div>
              </div>
              <div>
                <div style={{ color: "var(--text-muted)", fontSize: "11px", fontWeight: 700 }}>THREAT CATEGORY</div>
                <div style={{ fontWeight: 600, marginTop: "2px" }}>
                  {scan.threat_type || (scan.threat_types?.length ? scan.threat_types.join(", ") : "None")}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 3: Visual TreeSHAP Factor Breakdown + Raw Trace */}
        {activeSubTab === "ai-explanation" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "14px", marginBottom: "22px" }}>
            {parsed.factors.length > 0 && (
              <div style={{ background: "#f8fafc", border: "1px solid var(--card-border)", borderRadius: "12px", padding: "18px" }}>
                <h4 style={{ fontSize: "14px", fontWeight: 700, marginBottom: "14px" }}>
                  TreeSHAP Feature Contribution Impact
                </h4>
                <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                  {parsed.factors.map((f) => {
                    const widthPct = Math.max(8, Math.round((Math.abs(f.contribution) / maxAbsContribution) * 100));
                    const barColor = f.increasesRisk ? "var(--danger-red)" : "var(--safe-green)";
                    return (
                      <div key={f.feature}>
                        <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", marginBottom: "4px", gap: "8px", flexWrap: "wrap" }}>
                          <span style={{ fontWeight: 600, color: "var(--text-primary)" }}>{f.feature}</span>
                          <span style={{ fontFamily: "var(--font-mono)", fontWeight: 700, color: barColor }}>
                            {f.contribution >= 0 ? `+${f.contribution}` : f.contribution}
                          </span>
                        </div>
                        <div style={{ height: "7px", background: "#e2e8f0", borderRadius: "9999px", overflow: "hidden" }}>
                          <div style={{ width: `${widthPct}%`, height: "100%", background: barColor, borderRadius: "9999px" }} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            <div style={{ background: "#f8fafc", border: "1px solid var(--card-border)", borderRadius: "12px", padding: "18px" }}>
              <h4 style={{ fontSize: "13px", fontWeight: 700, marginBottom: "8px", color: "var(--text-secondary)" }}>
                Diagnostic Engine Output
              </h4>
              <pre style={{ margin: 0, fontSize: "12px", whiteSpace: "pre-wrap", wordBreak: "break-word", color: "var(--text-secondary)", fontFamily: "var(--font-mono)", lineHeight: 1.55 }}>
                {scan.explanation || "No extended explanation generated."}
              </pre>
            </div>
          </div>
        )}

        {/* Recommendation Banner */}
        {isSafe ? (
          <div className="recommendation-box-safe">
            <span style={{ flexShrink: 0 }}><ShieldCheckBadgeIcon size={20} /></span>
            <span><strong>Recommendation:</strong> You can visit this website safely.</span>
          </div>
        ) : isPhish ? (
          <div className="recommendation-box-danger">
            <span style={{ flexShrink: 0 }}><ShieldAlertBadgeIcon size={20} /></span>
            <span><strong>Recommendation:</strong> Do not enter any personal information, passwords, or credit card numbers.</span>
          </div>
        ) : (
          <div className="recommendation-box-warn">
            <span style={{ flexShrink: 0 }}><ShieldAlertBadgeIcon size={20} /></span>
            <span><strong>Recommendation:</strong> Treat this link as suspicious and avoid entering sensitive credentials.</span>
          </div>
        )}

        {onAskAboutScan && (
          <div className="result-action-row" style={{ justifyContent: "flex-end" }}>
            <button type="button" onClick={() => onAskAboutScan(scan)} className="btn-primary" style={{ minHeight: "42px", fontSize: "13px" }}>
              <AssistantIcon size={16} />
              Inquire with AI Assistant
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
