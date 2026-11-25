import React, { useEffect, useState } from "react";
import {
  BrandShieldIcon,
  LockIcon,
  PuzzleIcon,
  SettingsIcon,
  ShieldAlertBadgeIcon,
  ShieldCheckBadgeIcon,
} from "./Icons";

export function AccountSettings({ user, onRequireAuth }) {
  const [activeTab, setActiveTab] = useState("profile");
  const [editing, setEditing] = useState(false);
  const [displayName, setDisplayName] = useState(user?.full_name || "");
  const [profileSaved, setProfileSaved] = useState(false);
  const [passwordNotice, setPasswordNotice] = useState(false);
  const [extPreviewSafe, setExtPreviewSafe] = useState(true);

  useEffect(() => {
    setDisplayName(user?.full_name || "");
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
          <SettingsIcon size={28} />
        </div>
        <h2 style={{ fontSize: "20px", fontWeight: 700, marginBottom: "8px" }}>
          Authentication Required
        </h2>
        <p style={{ color: "var(--text-secondary)", maxWidth: "440px", margin: "0 auto 24px", fontSize: "14px" }}>
          Please sign in to manage your profile, authentication security, and Chrome Extension pairing.
        </p>
        <button type="button" onClick={onRequireAuth} className="btn-primary" style={{ padding: "10px 24px" }}>
          Sign In to Access Settings
        </button>
      </div>
    );
  }

  const effectiveName = displayName || user.full_name || "PhishGuard User";
  const initials = effectiveName
    .split(" ")
    .filter(Boolean)
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2) || user.email.slice(0, 2).toUpperCase();

  const handleToggleEdit = () => {
    if (editing) {
      setProfileSaved(true);
      setEditing(false);
    } else {
      setProfileSaved(false);
      setEditing(true);
    }
  };

  return (
    <div style={{ maxWidth: "840px", margin: "0 auto", display: "flex", flexDirection: "column", gap: "20px" }}>
      {/* Tabs (Profile, Security, Extension, Privacy) matching Board 9 */}
      <div
        style={{
          display: "flex",
          gap: "8px",
          borderBottom: "2px solid #e2e8f0",
          overflowX: "auto",
          WebkitOverflowScrolling: "touch",
        }}
        role="tablist"
      >
        {["profile", "security", "extension", "privacy"].map((tab) => {
          const active = activeTab === tab;
          return (
            <button
              key={tab}
              type="button"
              role="tab"
              aria-selected={active}
              onClick={() => setActiveTab(tab)}
              style={{
                background: "transparent",
                color: active ? "var(--color-primary)" : "var(--text-secondary)",
                border: "none",
                borderBottom: active ? "2px solid var(--color-primary)" : "2px solid transparent",
                marginBottom: "-2px",
                padding: "10px 16px",
                fontSize: "13px",
                fontWeight: active ? 700 : 600,
                cursor: "pointer",
                whiteSpace: "nowrap",
              }}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          );
        })}
      </div>

      {/* Main Card */}
      <div className="stat-card" style={{ padding: "clamp(18px, 3.5vw, 28px)" }}>
        {activeTab === "profile" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "22px" }}>
            {/* User Identity Row */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "16px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "14px", flex: "1 1 220px", minWidth: 0 }}>
                <div
                  style={{
                    width: "56px",
                    height: "56px",
                    borderRadius: "50%",
                    background: "var(--gradient-brand)",
                    color: "#ffffff",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: "20px",
                    fontWeight: 800,
                    flexShrink: 0,
                  }}
                >
                  {initials}
                </div>
                <div style={{ minWidth: 0, flex: 1 }}>
                  {editing ? (
                    <input
                      type="text"
                      className="scan-text-input"
                      style={{ padding: "6px 10px", fontSize: "15px", width: "100%", maxWidth: "240px" }}
                      value={displayName}
                      placeholder="Full Name"
                      onChange={(e) => setDisplayName(e.target.value)}
                    />
                  ) : (
                    <h3 style={{ fontSize: "18px", fontWeight: 700, margin: 0, color: "var(--text-primary)" }}>
                      {effectiveName}
                    </h3>
                  )}
                  <div style={{ fontSize: "13px", color: "var(--text-secondary)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {user.email}
                  </div>
                </div>
              </div>

              <button
                type="button"
                onClick={handleToggleEdit}
                className="filter-pill"
                style={{ padding: "8px 18px", fontSize: "13px", minHeight: "40px" }}
              >
                {editing ? "Save Profile" : "Edit Profile"}
              </button>
            </div>

            {profileSaved && (
              <div style={{ padding: "10px 14px", background: "var(--safe-bg)", border: "1px solid var(--safe-border)", color: "var(--safe-green-dark)", borderRadius: "10px", fontSize: "13px" }}>
                ✓ Display name updated for this session.
              </div>
            )}

            <hr style={{ border: "none", borderTop: "1px solid var(--card-border)" }} />

            {/* Change Password Row */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px" }}>
              <div>
                <div style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)" }}>
                  Change Password
                </div>
                <div style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
                  Protected with Argon2 password hashing
                </div>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
                <span style={{ fontSize: "16px", letterSpacing: "2px", color: "var(--text-secondary)" }}>••••••••••••</span>
                <button
                  type="button"
                  onClick={() => setPasswordNotice(!passwordNotice)}
                  className="btn-primary"
                  style={{ padding: "7px 14px", fontSize: "12px" }}
                >
                  Update
                </button>
              </div>
            </div>

            {passwordNotice && (
              <div style={{ padding: "10px 14px", background: "#eff6ff", border: "1px solid #bfdbfe", color: "#1d4ed8", borderRadius: "10px", fontSize: "13px" }}>
                Password rotation endpoint is managed via authenticated backend admin CLI in this local environment.
              </div>
            )}

            <hr style={{ border: "none", borderTop: "1px solid var(--card-border)" }} />

            {/* Connected Extension Row */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px" }}>
              <div>
                <div style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)" }}>
                  Connected Extension
                </div>
                <div style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
                  Chrome Manifest V3 browser protection status
                </div>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
                <span className="badge-pill-safe">● Ready</span>
                <button
                  type="button"
                  className="filter-pill"
                  style={{ padding: "6px 14px", fontSize: "12px" }}
                  onClick={() => setActiveTab("extension")}
                >
                  Manage
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === "security" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "14px", fontSize: "14px", color: "var(--text-secondary)", lineHeight: 1.6 }}>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", color: "var(--text-primary)" }}>
              <LockIcon size={20} />
              <h4 style={{ fontSize: "16px", fontWeight: 700, margin: 0 }}>Authentication & Session Security</h4>
            </div>
            <p>
              Sessions are issued using signed JWT tokens. Passwords are salted and hashed using Argon2 before persistence, and responses include strict security headers (<code>X-Content-Type-Options: nosniff</code>, <code>X-Frame-Options: DENY</code>).
            </p>
          </div>
        )}

        {/* Board 10: Interactive Chrome Extension Showcase + Setup Instructions */}
        {activeTab === "extension" && (
          <div className="grid-2-col" style={{ alignItems: "center" }}>
            <div style={{ display: "flex", flexDirection: "column", gap: "12px", fontSize: "14px", color: "var(--text-secondary)", lineHeight: 1.6 }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "var(--text-primary)" }}>
                <PuzzleIcon size={20} />
                <h4 style={{ fontSize: "16px", fontWeight: 700, margin: 0 }}>Chrome Extension Setup (Manifest V3)</h4>
              </div>
              <p>
                Real-time active-tab URL defense lives in <code>browser-extension/</code> using least-privilege permissions.
              </p>
              <ol style={{ paddingLeft: "18px", fontSize: "13px", display: "flex", flexDirection: "column", gap: "6px" }}>
                <li>Open <code>chrome://extensions</code> in Chrome and enable <strong>Developer Mode</strong>.</li>
                <li>Click <strong>Load unpacked</strong> and select the <code>browser-extension/</code> folder.</li>
                <li>Sign in via the extension popup gear menu to sync scans to your account history.</li>
              </ol>

              <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", marginTop: "6px" }}>
                <button
                  type="button"
                  className={`filter-pill ${extPreviewSafe ? "active" : ""}`}
                  style={{ fontSize: "12px" }}
                  onClick={() => setExtPreviewSafe(true)}
                >
                  Preview Safe State
                </button>
                <button
                  type="button"
                  className={`filter-pill ${!extPreviewSafe ? "active" : ""}`}
                  style={{ fontSize: "12px" }}
                  onClick={() => setExtPreviewSafe(false)}
                >
                  Preview Threat Alert
                </button>
              </div>
            </div>

            {/* Interactive Chrome Extension Mockup Frame matching Board 10 */}
            <div className="chrome-preview-shell">
              <div className="chrome-preview-toolbar">
                <div style={{ display: "flex", gap: "4px" }}>
                  <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#ef4444" }} />
                  <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#f59e0b" }} />
                  <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#10b981" }} />
                </div>
                <div className="chrome-address-bar">
                  {extPreviewSafe ? "https://www.google.com" : "http://login-secure-update.com"}
                </div>
                <div
                  style={{
                    width: "24px",
                    height: "24px",
                    borderRadius: "6px",
                    background: extPreviewSafe ? "var(--gradient-brand)" : "var(--danger-red)",
                    color: "#ffffff",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexShrink: 0,
                  }}
                >
                  <BrandShieldIcon size={14} />
                </div>
              </div>

              <div className="chrome-popup-body">
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <div className="brand-icon-shield" style={{ width: "26px", height: "26px", borderRadius: "7px" }}>
                      <BrandShieldIcon size={14} />
                    </div>
                    <strong style={{ fontSize: "14px" }}>
                      PhishGuard <span style={{ color: "var(--color-purple)" }}>X</span>
                    </strong>
                  </div>
                  <span style={{ color: "var(--text-muted)" }}><SettingsIcon size={15} /></span>
                </div>

                <div style={{ textAlign: "center" }}>
                  <div
                    className={extPreviewSafe ? "result-hero-icon-safe" : "result-hero-icon-danger"}
                    style={{ width: "44px", height: "44px", marginBottom: "10px" }}
                  >
                    {extPreviewSafe ? <ShieldCheckBadgeIcon size={22} /> : <ShieldAlertBadgeIcon size={22} />}
                  </div>
                  <div
                    style={{
                      fontSize: "15px",
                      fontWeight: 800,
                      color: extPreviewSafe ? "var(--safe-green-dark)" : "var(--danger-red-dark)",
                    }}
                  >
                    {extPreviewSafe ? "This website is safe!" : "Phishing Threat Blocked!"}
                  </div>
                  <div style={{ fontSize: "11px", color: "var(--text-secondary)", marginTop: "2px", wordBreak: "break-all" }}>
                    {extPreviewSafe ? "https://www.google.com" : "http://login-secure-update.com"}
                  </div>

                  <div
                    style={{
                      marginTop: "12px",
                      padding: "8px 10px",
                      borderRadius: "8px",
                      background: extPreviewSafe ? "var(--safe-bg)" : "var(--danger-bg)",
                      border: `1px solid ${extPreviewSafe ? "var(--safe-border)" : "var(--danger-border)"}`,
                      color: extPreviewSafe ? "var(--safe-green-dark)" : "var(--danger-red-dark)",
                      fontSize: "12px",
                      fontWeight: 600,
                    }}
                  >
                    {extPreviewSafe ? "Low risk detected · No threats found" : "High risk detected · Credential spoof"}
                  </div>

                  <div style={{ marginTop: "12px", fontSize: "12px", fontWeight: 600, color: "var(--color-primary)" }}>
                    View Details →
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === "privacy" && (
          <div style={{ fontSize: "14px", color: "var(--text-secondary)", lineHeight: 1.6 }}>
            <h4 style={{ fontSize: "16px", fontWeight: 700, color: "var(--text-primary)", marginBottom: "8px" }}>
              Data & Telemetry Controls
            </h4>
            <p>
              Authenticated URL scans are stored locally in your workspace database solely for your personal scan history, activity charts, and compliance exports. Guest scans remain unlinked to any user profile.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
