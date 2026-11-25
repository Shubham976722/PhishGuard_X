import React, { useEffect, useState } from "react";
import { Sidebar } from "./components/Sidebar";
import { LandingPage } from "./components/LandingPage";
import { UrlScanner } from "./components/UrlScanner";
import { Dashboard } from "./components/Dashboard";
import { ScanHistory } from "./components/ScanHistory";
import { ScanDetails } from "./components/ScanDetails";
import { Reports } from "./components/Reports";
import { AssistantChat } from "./components/AssistantChat";
import { AccountSettings } from "./components/AccountSettings";
import { AuthModal } from "./components/AuthModal";
import {
  BellIcon,
  MenuIcon,
  DashboardIcon,
  ScannerIcon,
  HistoryIcon,
  AssistantIcon,
  SettingsIcon,
} from "./components/Icons";
import { getProfile, logout, checkHealth } from "./services/api";

export function App() {
  const [activeTab, setActiveTab] = useState("landing");
  const [user, setUser] = useState(null);
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authInitialMode, setAuthInitialMode] = useState("login");
  const [systemReady, setSystemReady] = useState(false);
  const [selectedScan, setSelectedScan] = useState(null);
  const [initialScannerUrl, setInitialScannerUrl] = useState("");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);

  useEffect(() => {
    checkHealth()
      .then(() => setSystemReady(true))
      .catch(() => setSystemReady(false));

    getProfile()
      .then((u) => {
        setUser(u);
        setActiveTab("dashboard");
      })
      .catch(() => {
        setUser(null);
        setActiveTab("landing");
      });
  }, []);

  const handleLogout = () => {
    logout();
    setUser(null);
    setSelectedScan(null);
    setActiveTab("landing");
  };

  const handleAuthSuccess = () => {
    getProfile().then((u) => {
      setUser(u);
      setActiveTab("dashboard");
    });
  };

  const handleOpenAuth = (mode = "login") => {
    setAuthInitialMode(mode);
    setAuthModalOpen(true);
  };

  const handleQuickScanFromLanding = (url) => {
    setInitialScannerUrl(url);
    setActiveTab("scanner");
  };

  const handleSelectScanForDetails = (scan) => {
    setSelectedScan(scan);
    setActiveTab("scan-detail");
  };

  const handleAskAboutScan = (scan) => {
    setSelectedScan(scan);
    setActiveTab("assistant");
  };

  if (activeTab === "landing") {
    return (
      <>
        <LandingPage
          user={user}
          onQuickScan={handleQuickScanFromLanding}
          onOpenAuth={handleOpenAuth}
          onNavigateApp={(tab) => setActiveTab(tab)}
        />
        <AuthModal
          isOpen={authModalOpen}
          initialMode={authInitialMode}
          onClose={() => setAuthModalOpen(false)}
          onSuccess={handleAuthSuccess}
        />
      </>
    );
  }

  const tabTitles = {
    dashboard: { title: "Dashboard", sub: "Your security overview" },
    scanner: { title: "URL Scanner", sub: "Check any link for phishing and malware" },
    history: { title: "Scan History", sub: "Your past scans and threat telemetry" },
    "scan-detail": { title: "Scan Details", sub: "Comprehensive threat analysis and model breakdown" },
    reports: { title: "Security Reports", sub: "Generate and download compliance audit reports" },
    assistant: { title: "AI Security Assistant", sub: "Ask anything about cybersecurity and phishing" },
    settings: { title: "Account Settings", sub: "Manage your profile, security, and extension" },
  };

  const currentMeta = tabTitles[activeTab] || { title: "PhishGuard X", sub: "AI Threat Defense" };

  const bottomNavItems = [
    { id: "dashboard", label: "Dashboard", Icon: DashboardIcon },
    { id: "scanner", label: "Scanner", Icon: ScannerIcon },
    { id: "history", label: "History", Icon: HistoryIcon },
    { id: "assistant", label: "AI Chat", Icon: AssistantIcon },
    { id: "settings", label: "Settings", Icon: SettingsIcon },
  ];

  return (
    <div className="app-layout">
      <Sidebar
        activeTab={activeTab === "scan-detail" ? "history" : activeTab}
        isOpen={mobileMenuOpen}
        onClose={() => setMobileMenuOpen(false)}
        onTabChange={(tab) => {
          setSelectedScan(null);
          setActiveTab(tab);
          setMobileMenuOpen(false);
        }}
        onBackToHome={() => {
          setMobileMenuOpen(false);
          setActiveTab("landing");
        }}
        onLogout={handleLogout}
        user={user}
      />

      <div className="main-viewport">
        <header className="top-app-bar">
          <div className="top-bar-left">
            <button
              type="button"
              className="mobile-menu-btn"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label="Open navigation menu"
            >
              <MenuIcon size={20} />
            </button>
            <div style={{ minWidth: 0 }}>
              <h1 className="top-bar-title">{currentMeta.title}</h1>
              <span className="top-bar-sub">{currentMeta.sub}</span>
            </div>
          </div>

          <div className="top-bar-right">
            {activeTab !== "scanner" && (
              <button
                type="button"
                className="top-quick-scan-btn"
                onClick={() => {
                  setInitialScannerUrl("");
                  setActiveTab("scanner");
                }}
              >
                <ScannerIcon size={15} />
                Quick Scan
              </button>
            )}

            <button
              type="button"
              className="icon-circle-btn"
              onClick={() => setNotifOpen(!notifOpen)}
              aria-label="System status notifications"
              title={systemReady ? "Backend Engine Ready" : "Backend Disconnected"}
            >
              <BellIcon size={18} />
              <span
                className="status-ping-dot"
                style={{ background: systemReady ? "var(--safe-green)" : "var(--danger-red)" }}
              />
            </button>

            {notifOpen && (
              <div className="notif-popover">
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                  <strong style={{ fontSize: "13px" }}>Security Telemetry</strong>
                  <span className={systemReady ? "badge-pill-safe" : "badge-pill-danger"} style={{ fontSize: "11px" }}>
                    {systemReady ? "Online" : "Offline"}
                  </span>
                </div>
                <p style={{ fontSize: "12px", color: "var(--text-secondary)", lineHeight: 1.45, marginBottom: "10px" }}>
                  {systemReady
                    ? "FastAPI detection engine, LightGBM scoring pipeline, and local threat feeds are active."
                    : "Unable to verify /api/v1/health/ready. Make sure the backend server is running."}
                </p>
                <button
                  type="button"
                  className="filter-pill"
                  style={{ width: "100%", justifyContent: "center", fontSize: "12px" }}
                  onClick={() => {
                    setNotifOpen(false);
                    setActiveTab("scanner");
                  }}
                >
                  Open URL Scanner
                </button>
              </div>
            )}

            {user ? (
              <button
                type="button"
                onClick={() => setActiveTab("settings")}
                title={user.full_name || user.email}
                aria-label="Account Settings"
                style={{
                  width: "38px",
                  height: "38px",
                  borderRadius: "50%",
                  border: "none",
                  background: "var(--gradient-brand)",
                  color: "#ffffff",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "13px",
                  fontWeight: 700,
                  cursor: "pointer",
                  flexShrink: 0,
                }}
              >
                {user.full_name ? user.full_name.charAt(0).toUpperCase() : user.email.charAt(0).toUpperCase()}
              </button>
            ) : (
              <button
                type="button"
                onClick={() => handleOpenAuth("login")}
                className="btn-primary"
                style={{ padding: "8px 16px", fontSize: "13px", minHeight: "38px" }}
              >
                Sign In
              </button>
            )}
          </div>
        </header>

        <main className="content-body">
          {activeTab === "dashboard" && (
            <Dashboard
              user={user}
              onRequireAuth={() => handleOpenAuth("login")}
              onNavigateTab={setActiveTab}
              onSelectScan={handleSelectScanForDetails}
            />
          )}

          {activeTab === "scanner" && (
            <UrlScanner
              user={user}
              initialUrl={initialScannerUrl}
              onRequireAuth={() => handleOpenAuth("login")}
              onAskAboutScan={handleAskAboutScan}
            />
          )}

          {activeTab === "history" && (
            <ScanHistory
              user={user}
              onRequireAuth={() => handleOpenAuth("login")}
              onSelectScan={handleSelectScanForDetails}
            />
          )}

          {activeTab === "scan-detail" && (
            <ScanDetails
              scan={selectedScan}
              onBack={() => setActiveTab("history")}
              onAskAboutScan={handleAskAboutScan}
            />
          )}

          {activeTab === "reports" && (
            <Reports
              user={user}
              onRequireAuth={() => handleOpenAuth("login")}
            />
          )}

          {activeTab === "assistant" && (
            <AssistantChat
              user={user}
              onRequireAuth={() => handleOpenAuth("login")}
              initialScan={selectedScan}
            />
          )}

          {activeTab === "settings" && (
            <AccountSettings
              user={user}
              onRequireAuth={() => handleOpenAuth("login")}
              onLogout={handleLogout}
            />
          )}
        </main>
      </div>

      <nav className="mobile-bottom-nav" aria-label="Mobile Quick Navigation">
        {bottomNavItems.map(({ id, label, Icon }) => {
          const isActive = activeTab === id || (id === "history" && activeTab === "scan-detail");
          return (
            <button
              key={id}
              type="button"
              className={`mobile-bottom-item ${isActive ? "active" : ""}`}
              onClick={() => {
                setSelectedScan(null);
                setActiveTab(id);
              }}
              aria-current={isActive ? "page" : undefined}
            >
              <Icon size={20} />
              <span>{label}</span>
            </button>
          );
        })}
      </nav>

      <AuthModal
        isOpen={authModalOpen}
        initialMode={authInitialMode}
        onClose={() => setAuthModalOpen(false)}
        onSuccess={handleAuthSuccess}
      />
    </div>
  );
}

export default App;
