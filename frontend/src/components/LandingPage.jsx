import React, { useState } from "react";
import {
  BrandShieldIcon,
  HeroShieldArtwork,
  MenuIcon,
  CloseIcon,
  ScannerIcon,
  AssistantIcon,
  HistoryIcon,
  PuzzleIcon,
  SparklesIcon,
} from "./Icons";

const FAQ_ITEMS = [
  {
    q: "How does PhishGuard X detect zero-day phishing websites?",
    a: "PhishGuard X combines instant threat-intelligence feed lookups with a LightGBM machine learning classifier trained on 14 lexical URL structure and domain signals, catching never-before-seen phishing links even when blocklists do not list them yet.",
  },
  {
    q: "What is TreeSHAP explainability in the scan breakdown?",
    a: "Instead of returning a black-box verdict, our backend computes exact feature-level TreeSHAP contributions for every URL (such as HTTPS absence, IP hostnames, suspicious tokens, and Punycode obfuscation) so you know why a link was flagged.",
  },
  {
    q: "How does the Chrome Extension work with the web dashboard?",
    a: "The Manifest V3 browser extension inspects active tabs in real time using least-privilege permissions and pairs directly with your PhishGuard X account to sync scan history and detailed telemetry.",
  },
  {
    q: "Can I export security scan logs for audits?",
    a: "Yes. Authenticated users can filter scan history by date range or verdict and export detailed compliance reports in CSV, JSON, or printable PDF summary format.",
  },
];

export function LandingPage({ user, onQuickScan, onOpenAuth, onNavigateApp }) {
  const [url, setUrl] = useState("");
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [openFaq, setOpenFaq] = useState(0);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (url.trim()) {
      onQuickScan(url.trim());
    }
  };

  const handleNav = (tab) => {
    setMobileNavOpen(false);
    onNavigateApp(tab);
  };

  const handleAuth = (mode) => {
    setMobileNavOpen(false);
    onOpenAuth(mode);
  };

  const handleSampleScan = (sampleUrl) => {
    setUrl(sampleUrl);
    onQuickScan(sampleUrl);
  };

  return (
    <div id="home" className="landing-shell">
      {/* Sticky Responsive Navbar (Board 1) */}
      <header className="landing-nav">
        <div className="container landing-nav-inner">
          <div className="brand-group" onClick={() => handleNav("landing")}>
            <div className="brand-icon-shield">
              <BrandShieldIcon size={20} />
            </div>
            <div className="brand-title">
              PhishGuard <span>X</span>
            </div>
          </div>

          <button
            type="button"
            className="landing-nav-toggle"
            onClick={() => setMobileNavOpen(!mobileNavOpen)}
            aria-label={mobileNavOpen ? "Close menu" : "Open menu"}
            aria-expanded={mobileNavOpen}
          >
            {mobileNavOpen ? <CloseIcon size={20} /> : <MenuIcon size={20} />}
          </button>

          <nav className={`landing-menu ${mobileNavOpen ? "open" : ""}`} aria-label="Landing Navigation">
            <a href="#home" className="landing-nav-link" onClick={() => setMobileNavOpen(false)}>Home</a>
            <a href="#features" className="landing-nav-link" onClick={() => setMobileNavOpen(false)}>Features</a>
            <a href="#about" className="landing-nav-link" onClick={() => setMobileNavOpen(false)}>About</a>
            <a href="#faq" className="landing-nav-link" onClick={() => setMobileNavOpen(false)}>FAQ</a>

            <div className="landing-auth-actions">
              {user ? (
                <button
                  type="button"
                  onClick={() => handleNav("dashboard")}
                  className="btn-primary"
                  style={{ padding: "8px 18px", fontSize: "14px" }}
                >
                  Open Dashboard
                </button>
              ) : (
                <>
                  <button
                    type="button"
                    onClick={() => handleAuth("login")}
                    className="btn-outline-nav"
                  >
                    Login
                  </button>
                  <button
                    type="button"
                    onClick={() => handleAuth("register")}
                    className="btn-primary"
                    style={{ padding: "9px 20px", fontSize: "14px" }}
                  >
                    Sign Up
                  </button>
                </>
              )}
            </div>
          </nav>
        </div>
      </header>

      {/* Hero Section (Board 1) */}
      <section className="landing-hero-wrapper">
        <div className="container">
          <div className="landing-hero">
            <div>
              <div className="hero-badge-pill">
                <SparklesIcon size={14} />
                <span>Real-Time AI URL Intelligence</span>
              </div>

              <h1 className="hero-heading">
                Browse safely.
                <br />
                <span className="hero-heading-accent">Stay protected.</span>
              </h1>

              <p className="hero-sub">
                AI-powered phishing detection and browser protection for a safer internet.
                Analyze suspicious URLs in milliseconds using LightGBM, threat intelligence feeds, and TreeSHAP explainability.
              </p>

              <form onSubmit={handleSubmit} className="hero-search-box">
                <input
                  type="text"
                  className="hero-search-input"
                  placeholder="Enter a URL to check (e.g. https://example.com)..."
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  aria-label="URL to inspect"
                />
                <button type="submit" className="hero-search-btn">
                  Scan Now
                </button>
              </form>

              <div className="hero-quick-samples">
                <span style={{ fontWeight: 600 }}>Try quick scan:</span>
                <button
                  type="button"
                  className="sample-chip-btn"
                  onClick={() => handleSampleScan("https://github.com")}
                >
                  github.com
                </button>
                <button
                  type="button"
                  className="sample-chip-btn"
                  onClick={() => handleSampleScan("http://login-secure-update.com")}
                >
                  login-secure-update.com
                </button>
                <button
                  type="button"
                  className="sample-chip-btn"
                  onClick={() => handleSampleScan("http://192.168.1.10/bank/login/verify")}
                >
                  192.168.1.10/bank/verify
                </button>
              </div>

              <div className="hero-trust-row">
                <span>✓ Active Threat Intel Feeds</span>
                <span>✓ 14-Feature LightGBM Engine</span>
                <span>✓ TreeSHAP + Local RAG</span>
              </div>
            </div>

            {/* 3D Glowing Shield + Orbital Artwork */}
            <div className="shield-visual-container">
              <div className="shield-stage">
                <div className="hero-float-badge top-left">
                  <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "var(--safe-green)" }} />
                  <span>Zero-Day ML Guard</span>
                </div>
                <HeroShieldArtwork />
                <div className="hero-float-badge bottom-right">
                  <span style={{ color: "var(--color-purple)" }}>⚡</span>
                  <span>Explainable Risk Score</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Soft Wave Divider matching Board 1 */}
        <div className="landing-wave-divider" aria-hidden="true">
          <svg viewBox="0 0 1440 90" preserveAspectRatio="none">
            <path
              fill="#ffffff"
              d="M0,48 C240,86 480,10 720,44 C960,78 1200,18 1440,52 L1440,90 L0,90 Z"
            />
          </svg>
        </div>
      </section>

      {/* 4 Core Feature Cards (Board 1) */}
      <section id="features" className="landing-white-band" style={{ borderTop: "none", paddingTop: "24px" }}>
        <div className="container">
          <div className="feature-cards-grid">
            <div
              className="feature-card"
              onClick={() => onNavigateApp("scanner")}
              onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && onNavigateApp("scanner")}
              role="button"
              tabIndex={0}
            >
              <div className="feature-card-icon" style={{ background: "rgba(37, 99, 235, 0.1)", color: "var(--color-primary)" }}>
                <ScannerIcon size={22} />
              </div>
              <h3 style={{ fontSize: "16px", fontWeight: 700, marginBottom: "6px" }}>URL Protection</h3>
              <p style={{ fontSize: "13px", color: "var(--text-secondary)", lineHeight: 1.55 }}>
                ML + Threat Intel. Real-time lexical feature scanning paired with verified phishing feeds.
              </p>
            </div>

            <div
              className="feature-card"
              onClick={() => onNavigateApp("assistant")}
              onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && onNavigateApp("assistant")}
              role="button"
              tabIndex={0}
            >
              <div className="feature-card-icon" style={{ background: "rgba(99, 102, 241, 0.12)", color: "var(--color-purple)" }}>
                <AssistantIcon size={22} />
              </div>
              <h3 style={{ fontSize: "16px", fontWeight: 700, marginBottom: "6px" }}>AI Explanation</h3>
              <p style={{ fontSize: "13px", color: "var(--text-secondary)", lineHeight: 1.55 }}>
                Understand Risks. Grounded RAG security assistant translates TreeSHAP scores into plain advice.
              </p>
            </div>

            <div
              className="feature-card"
              onClick={() => onNavigateApp("history")}
              onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && onNavigateApp("history")}
              role="button"
              tabIndex={0}
            >
              <div className="feature-card-icon" style={{ background: "var(--safe-bg)", color: "var(--safe-green)" }}>
                <HistoryIcon size={22} />
              </div>
              <h3 style={{ fontSize: "16px", fontWeight: 700, marginBottom: "6px" }}>Scan History</h3>
              <p style={{ fontSize: "13px", color: "var(--text-secondary)", lineHeight: 1.55 }}>
                Track Activity. Review past scans, risk confidence timelines, and export audit logs.
              </p>
            </div>

            <div
              className="feature-card"
              onClick={() => onNavigateApp("settings")}
              onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && onNavigateApp("settings")}
              role="button"
              tabIndex={0}
            >
              <div className="feature-card-icon" style={{ background: "var(--amber-bg)", color: "var(--amber-warn-dark)" }}>
                <PuzzleIcon size={22} />
              </div>
              <h3 style={{ fontSize: "16px", fontWeight: 700, marginBottom: "6px" }}>Browser Protection</h3>
              <p style={{ fontSize: "13px", color: "var(--text-secondary)", lineHeight: 1.55 }}>
                Chrome Extension. Instant active-tab warnings before you type credentials on spoofed sites.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* About / How It Works Section */}
      <section id="about" style={{ padding: "clamp(36px, 5vw, 64px) 0", background: "var(--canvas-bg)", borderTop: "1px solid var(--card-border)" }}>
        <div className="container">
          <div className="section-header-center">
            <h2>Multi-Tiered Defense Pipeline</h2>
            <p>Every scanned URL passes through deterministic extraction, ensemble inference, and threat correlation.</p>
          </div>

          <div className="pipeline-steps-grid">
            <div className="pipeline-step-card">
              <div className="step-number-pill">1</div>
              <h3 style={{ fontSize: "16px", fontWeight: 700, marginBottom: "8px" }}>Lexical Feature Extraction</h3>
              <p style={{ fontSize: "13px", color: "var(--text-secondary)", lineHeight: 1.6 }}>
                Extracts 14 pure URL structural traits including hostname length, Punycode encodings, IP-in-host usage, HTTPS presence, and suspicious tokens.
              </p>
            </div>

            <div className="pipeline-step-card">
              <div className="step-number-pill">2</div>
              <h3 style={{ fontSize: "16px", fontWeight: 700, marginBottom: "8px" }}>LightGBM + Threat Intel</h3>
              <p style={{ fontSize: "13px", color: "var(--text-secondary)", lineHeight: 1.6 }}>
                Evaluates phishing probability using LightGBM while cross-checking exact URL and hostname indicators against active threat intelligence sources.
              </p>
            </div>

            <div className="pipeline-step-card">
              <div className="step-number-pill">3</div>
              <h3 style={{ fontSize: "16px", fontWeight: 700, marginBottom: "8px" }}>Explainable AI Guidance</h3>
              <p style={{ fontSize: "13px", color: "var(--text-secondary)", lineHeight: 1.6 }}>
                Surfaces per-feature TreeSHAP contributions alongside a cybersecurity RAG assistant so every verdict is transparent and actionable.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="landing-white-band">
        <div className="container">
          <div className="section-header-center">
            <h2>Frequently Asked Questions</h2>
            <p>Quick answers on detection accuracy, privacy, and browser extension integration.</p>
          </div>

          <div className="faq-list">
            {FAQ_ITEMS.map((item, idx) => {
              const isOpen = openFaq === idx;
              return (
                <div key={item.q} className={`faq-item ${isOpen ? "open" : ""}`}>
                  <button
                    type="button"
                    className="faq-trigger"
                    onClick={() => setOpenFaq(isOpen ? -1 : idx)}
                    aria-expanded={isOpen}
                  >
                    <span>{item.q}</span>
                    <span style={{ color: "var(--color-purple)", fontSize: "18px", fontWeight: 700, flexShrink: 0 }}>
                      {isOpen ? "−" : "+"}
                    </span>
                  </button>
                  {isOpen && <div className="faq-answer">{item.a}</div>}
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <footer
        style={{
          background: "#ffffff",
          borderTop: "1px solid var(--card-border)",
          padding: "24px 0",
          fontSize: "13px",
          color: "var(--text-secondary)",
        }}
      >
        <div className="container" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px" }}>
          <span>PhishGuard X — AI-Powered Phishing Protection Platform</span>
          <div style={{ display: "flex", gap: "16px", flexWrap: "wrap" }}>
            <button type="button" onClick={() => handleNav("scanner")} style={{ background: "none", border: "none", color: "var(--text-secondary)", cursor: "pointer", fontSize: "13px" }}>
              Scanner
            </button>
            <button type="button" onClick={() => handleNav("dashboard")} style={{ background: "none", border: "none", color: "var(--text-secondary)", cursor: "pointer", fontSize: "13px" }}>
              Dashboard
            </button>
            <button type="button" onClick={() => handleNav("settings")} style={{ background: "none", border: "none", color: "var(--text-secondary)", cursor: "pointer", fontSize: "13px" }}>
              Extension
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
}
