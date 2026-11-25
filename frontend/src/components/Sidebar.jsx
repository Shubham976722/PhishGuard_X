import React from "react";
import {
  BrandShieldIcon,
  DashboardIcon,
  ScannerIcon,
  HistoryIcon,
  ReportsIcon,
  AssistantIcon,
  SettingsIcon,
  LogoutIcon,
  CloseIcon,
} from "./Icons";

export function Sidebar({ activeTab, onTabChange, onLogout, user, isOpen, onClose, onBackToHome }) {
  const navItems = [
    { id: "dashboard", label: "Dashboard", Icon: DashboardIcon },
    { id: "scanner", label: "URL Scanner", Icon: ScannerIcon },
    { id: "history", label: "Scan History", Icon: HistoryIcon },
    { id: "reports", label: "Reports", Icon: ReportsIcon },
    { id: "assistant", label: "AI Assistant", Icon: AssistantIcon },
    { id: "settings", label: "Settings", Icon: SettingsIcon },
  ];

  const handleNavClick = (id) => {
    onTabChange(id);
    if (onClose) onClose();
  };

  const handleLogoutClick = () => {
    if (onClose) onClose();
    if (user) {
      onLogout();
    } else if (onBackToHome) {
      onBackToHome();
    }
  };

  return (
    <>
      <div
        className={`sidebar-overlay ${isOpen ? "open" : ""}`}
        onClick={onClose}
        aria-hidden="true"
      />

      <aside className={`sidebar ${isOpen ? "open" : ""}`} aria-label="Primary Sidebar Navigation">
        <div className="sidebar-brand">
          <div className="sidebar-brand-inner" onClick={() => (onBackToHome ? onBackToHome() : handleNavClick("dashboard"))}>
            <div className="brand-icon-shield">
              <BrandShieldIcon size={20} />
            </div>
            <div style={{ display: "flex", flexDirection: "column" }}>
              <span style={{ fontSize: "16px", fontWeight: 800, color: "#ffffff", letterSpacing: "-0.02em" }}>
                PhishGuard <span style={{ color: "#818cf8" }}>X</span>
              </span>
              <span style={{ fontSize: "10px", color: "var(--navy-sidebar-text)", textTransform: "uppercase", letterSpacing: "0.9px" }}>
                AI Threat Defense
              </span>
            </div>
          </div>

          <button
            type="button"
            className="sidebar-close-btn"
            onClick={onClose}
            aria-label="Close navigation menu"
          >
            <CloseIcon size={18} />
          </button>
        </div>

        <nav className="sidebar-nav">
          {navItems.map(({ id, label, Icon }) => {
            const isActive = activeTab === id;
            return (
              <button
                key={id}
                type="button"
                className={`nav-link-btn ${isActive ? "active" : ""}`}
                onClick={() => handleNavClick(id)}
                aria-current={isActive ? "page" : undefined}
              >
                <span style={{ display: "flex", alignItems: "center", flexShrink: 0 }}>
                  <Icon size={18} />
                </span>
                <span style={{ flex: 1 }}>{label}</span>
              </button>
            );
          })}
        </nav>

        <div className="sidebar-bottom">
          {user && (
            <div
              onClick={() => handleNavClick("settings")}
              style={{
                padding: "8px 10px 12px",
                display: "flex",
                alignItems: "center",
                gap: "10px",
                cursor: "pointer",
                borderRadius: "8px",
              }}
            >
              <div
                style={{
                  width: "32px",
                  height: "32px",
                  borderRadius: "50%",
                  background: "var(--gradient-brand)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "#ffffff",
                  fontWeight: 700,
                  fontSize: "12px",
                  flexShrink: 0,
                }}
              >
                {user.full_name ? user.full_name.charAt(0).toUpperCase() : user.email.charAt(0).toUpperCase()}
              </div>
              <div style={{ overflow: "hidden", minWidth: 0 }}>
                <div style={{ fontSize: "12px", color: "#ffffff", fontWeight: 600, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {user.full_name || "Active User"}
                </div>
                <div style={{ fontSize: "11px", color: "var(--navy-sidebar-text)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {user.email}
                </div>
              </div>
            </div>
          )}

          <button
            type="button"
            className="nav-link-btn"
            onClick={handleLogoutClick}
            style={{ color: user ? "#f87171" : "var(--navy-sidebar-text)" }}
          >
            <span style={{ display: "flex", alignItems: "center", flexShrink: 0 }}>
              <LogoutIcon size={18} />
            </span>
            <span>{user ? "Logout" : "Landing Home"}</span>
          </button>
        </div>
      </aside>
    </>
  );
}
