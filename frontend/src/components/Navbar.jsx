import React from "react";

export function Navbar({ activeTab, onTabChange, user, onOpenAuth, onLogout, systemReady }) {
  return (
    <header className="navbar">
      <div className="container navbar-inner">
        <div className="brand-link" onClick={() => onTabChange("scanner")}>
          <img src="/icons/icon.svg" alt="PhishGuard X Logo" className="brand-logo" />
          <div className="brand-name">
            PhishGuard <span>X</span>
          </div>
        </div>

        <nav className="nav-links">
          <button
            className={`nav-item ${activeTab === "scanner" ? "active" : ""}`}
            onClick={() => onTabChange("scanner")}
          >
            Scanner
          </button>
          <button
            className={`nav-item ${activeTab === "dashboard" ? "active" : ""}`}
            onClick={() => onTabChange("dashboard")}
          >
            Dashboard
          </button>
          <button
            className={`nav-item ${activeTab === "history" ? "active" : ""}`}
            onClick={() => onTabChange("history")}
          >
            History
          </button>
          <button
            className={`nav-item ${activeTab === "reports" ? "active" : ""}`}
            onClick={() => onTabChange("reports")}
          >
            Reports
          </button>
          <button
            className={`nav-item ${activeTab === "assistant" ? "active" : ""}`}
            onClick={() => onTabChange("assistant")}
          >
            AI Assistant
          </button>
        </nav>

        <div className="auth-btn-group">
          <span
            className={`status-dot ${systemReady ? "online" : "offline"}`}
            title={systemReady ? "Backend Connected" : "Backend Disconnected"}
          />
          {user ? (
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <span className="mono" style={{ fontSize: "12px", color: "var(--color-brand)" }}>
                {user.email}
              </span>
              <button className="btn btn-secondary btn-sm" onClick={onLogout}>
                Sign Out
              </button>
            </div>
          ) : (
            <button className="btn btn-primary btn-sm" onClick={onOpenAuth}>
              Sign In
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
