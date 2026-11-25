import React from "react";
import { getScanDisplayMetrics, parseScanExplanation } from "../utils/scanHelpers";
import {
  AssistantIcon,
  ShieldAlertBadgeIcon,
  ShieldCheckBadgeIcon,
} from "./Icons";

export function ScanResult({ scan, onAskAboutScan, onReset }) {
  if (!scan) return null;

  const { isSafe, isPhish, statusKey, confidence } = getScanDisplayMetrics(scan);
  const parsed = parseScanExplanation(scan.explanation);
  const hasHttps = typeof scan.url === "string" && scan.url.toLowerCase().startsWith("https://");
  const hasThreatMatches = Array.isArray(scan.threat_sources) && scan.threat_sources.length > 0;

  const cardClass =
    statusKey === "safe"
      ? "result-card-safe"
      : statusKey === "danger"
        ? "result-card-danger"
        : "result-card-warn";

  const iconClass =
    statusKey === "safe"
      ? "result-hero-icon-safe"
      : statusKey === "danger"
        ? "result-hero-icon-danger"
        : "result-hero-icon-warn";

  const headlineClass =
    statusKey === "safe"
      ? "result-headline-safe"
      : statusKey === "danger"
        ? "result-headline-danger"
        : "result-headline-warn";

  const fillClass =
    statusKey === "safe"
      ? "confidence-fill-safe"
      : statusKey === "danger"
        ? "confidence-fill-danger"
        : "confidence-fill-warn";

  // Build dynamic "Why?" reasons from real backend explanation & threat intel
  const reasons = [];
  if (hasThreatMatches) {
    reasons.push({
      tone: "danger",
      text: `Found in verified threat intelligence feeds (${scan.threat_sources.join(", ")})`,
    });
  } else if (isSafe) {
    reasons.push({
      tone: "safe",
      text: "Not listed in verified threat intelligence feeds",
    });
  }

  if (parsed.factors.length > 0) {
    for (const item of parsed.factors.slice(0, 3)) {
      reasons.push({
        tone: item.increasesRisk ? (isSafe ? "warn" : "danger") : "safe",
        text: `${item.feature}: ${item.impactText} (${item.contribution >= 0 ? "+" : ""}${item.contribution})`,
      });
    }
  } else if (isSafe) {
    reasons.push({ tone: "safe", text: "No malicious indicators found" });
    reasons.push({ tone: "safe", text: "Normal domain and URL path characteristics" });
  } else {
    reasons.push({ tone: "danger", text: "Suspicious URL and lexical token characteristics" });
    reasons.push({ tone: "danger", text: "Elevated LightGBM phishing probability detected" });
  }

  return (
    <div className={cardClass}>
      {/* Hero Icon */}
      <div className={iconClass}>
        {isSafe ? <ShieldCheckBadgeIcon size={30} /> : <ShieldAlertBadgeIcon size={30} />}
      </div>

      {/* Headline & Subline (Boards 2 & 3) */}
      <h2 className={headlineClass}>
        {isSafe
          ? "This website looks safe!"
          : isPhish
            ? "Potential Phishing Website!"
            : "Suspicious Website Detected!"}
      </h2>
      <p className="result-subline">
        {isSafe
          ? "Low risk detected."
          : isPhish
            ? "High risk detected."
            : "Medium risk detected. Verify domain authenticity carefully."}
      </p>

      {/* Confidence Bar */}
      <div className="confidence-wrap">
        <div className="confidence-header">
          <span style={{ color: "var(--text-primary)" }}>Confidence: {confidence}%</span>
          <span style={{ color: "var(--text-secondary)", fontSize: "12px" }}>
            Target: <code>{scan.url}</code>
          </span>
        </div>
        <div className="confidence-track">
          <div
            className={fillClass}
            style={{ width: `${Math.max(8, Math.min(100, Number(confidence)))}%` }}
          />
        </div>
      </div>

      {/* Quick 4-Signal Security Snapshot */}
      <div className="signal-mini-grid">
        <div className="signal-mini-box">
          <div style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: 600 }}>PROTOCOL</div>
          <div style={{ fontSize: "13px", fontWeight: 700, color: hasHttps ? "var(--safe-green-dark)" : "var(--amber-warn-dark)", marginTop: "2px" }}>
            {hasHttps ? "HTTPS Encrypted" : "Insecure HTTP"}
          </div>
        </div>

        <div className="signal-mini-box">
          <div style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: 600 }}>THREAT INTEL</div>
          <div style={{ fontSize: "13px", fontWeight: 700, color: hasThreatMatches ? "var(--danger-red-dark)" : "var(--safe-green-dark)", marginTop: "2px" }}>
            {hasThreatMatches ? `${scan.threat_sources.length} Feed Match` : "0 Blacklist Hits"}
          </div>
        </div>

        <div className="signal-mini-box">
          <div style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: 600 }}>RISK LEVEL</div>
          <div style={{ fontSize: "13px", fontWeight: 700, color: "var(--text-primary)", textTransform: "capitalize", marginTop: "2px" }}>
            {scan.risk_level || (isSafe ? "low" : "high")}
          </div>
        </div>

        <div className="signal-mini-box">
          <div style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: 600 }}>ML ENGINE</div>
          <div style={{ fontSize: "13px", fontWeight: 700, color: "var(--color-primary)", marginTop: "2px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
            {parsed.modelName}
          </div>
        </div>
      </div>

      {/* Why? Section (TreeSHAP + Feeds) */}
      <div className="why-section">
        <h3 className="why-title">Why?</h3>
        <ul className="why-list">
          {reasons.map((r, index) => (
            <li key={index} className="why-item">
              <span
                style={{
                  color:
                    r.tone === "safe"
                      ? "var(--safe-green)"
                      : r.tone === "danger"
                        ? "var(--danger-red)"
                        : "var(--amber-warn-dark)",
                  fontWeight: 800,
                  flexShrink: 0,
                  marginTop: "1px",
                }}
              >
                {r.tone === "safe" ? "✓" : "!"}
              </span>
              <span>{r.text}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Recommendation Box */}
      {isSafe ? (
        <div className="recommendation-box-safe">
          <span style={{ flexShrink: 0 }}>
            <ShieldCheckBadgeIcon size={20} />
          </span>
          <span>
            <strong>Recommendation:</strong> You can visit this website safely.
          </span>
        </div>
      ) : isPhish ? (
        <div className="recommendation-box-danger">
          <span style={{ flexShrink: 0 }}>
            <ShieldAlertBadgeIcon size={20} />
          </span>
          <span>
            <strong>Recommendation:</strong> Do not enter any personal information, passwords, or banking details.
          </span>
        </div>
      ) : (
        <div className="recommendation-box-warn">
          <span style={{ flexShrink: 0 }}>
            <ShieldAlertBadgeIcon size={20} />
          </span>
          <span>
            <strong>Recommendation:</strong> Exercise caution and verify the official domain before signing in.
          </span>
        </div>
      )}

      {/* Action Buttons */}
      <div className="result-action-row">
        {onReset && (
          <button type="button" onClick={onReset} className="filter-pill" style={{ minHeight: "42px", padding: "9px 18px" }}>
            ← Scan Another Link
          </button>
        )}
        {onAskAboutScan && (
          <button
            type="button"
            onClick={() => onAskAboutScan(scan)}
            className="btn-primary"
            style={{ minHeight: "42px", padding: "9px 18px", fontSize: "13px", marginLeft: "auto" }}
          >
            <AssistantIcon size={16} />
            Ask AI Assistant
          </button>
        )}
      </div>
    </div>
  );
}
