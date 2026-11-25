import React, { useEffect, useState } from "react";
import { login, register } from "../services/api";
import { BrandShieldIcon, CloseIcon, LaptopShieldArtwork } from "./Icons";

export function AuthModal({ isOpen, onClose, onSuccess, initialMode = "login" }) {
  const [mode, setMode] = useState(initialMode);
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [infoNotice, setInfoNotice] = useState(null);

  useEffect(() => {
    if (isOpen) {
      setMode(initialMode);
      setError(null);
      setInfoNotice(null);
    }
  }, [initialMode, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setInfoNotice(null);
    setLoading(true);

    try {
      if (mode === "register") {
        await register(fullName, email, password);
        await login(email, password);
      } else {
        await login(email, password);
      }
      onSuccess();
      onClose();
    } catch (err) {
      setError(err.message || "Authentication failed. Please verify your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose} role="dialog" aria-modal="true" aria-label="Account Authentication">
      <div className="split-auth-card" onClick={(e) => e.stopPropagation()}>
        {/* Mobile Brand Banner (Visible <= 768px) */}
        <div className="split-auth-mobile-banner">
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div className="brand-icon-shield" style={{ width: "32px", height: "32px" }}>
              <BrandShieldIcon size={18} />
            </div>
            <div>
              <div style={{ fontSize: "15px", fontWeight: 800 }}>
                PhishGuard <span style={{ color: "#a5b4fc" }}>X</span>
              </div>
              <div style={{ fontSize: "11px", color: "rgba(255,255,255,0.75)" }}>
                AI-Powered Threat Protection
              </div>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            aria-label="Close modal"
            style={{
              background: "rgba(255,255,255,0.12)",
              border: "none",
              color: "#ffffff",
              width: "36px",
              height: "36px",
              borderRadius: "8px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              cursor: "pointer",
            }}
          >
            <CloseIcon size={16} />
          </button>
        </div>

        {/* Left Desktop Brand Graphic (Board 11) */}
        <div className="split-auth-graphic">
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div className="brand-icon-shield">
              <BrandShieldIcon size={20} />
            </div>
            <div style={{ fontSize: "18px", fontWeight: 800, color: "#ffffff" }}>
              PhishGuard <span style={{ color: "#a5b4fc" }}>X</span>
            </div>
          </div>

          <div style={{ margin: "28px 0", textAlign: "center" }}>
            <h3 style={{ fontSize: "21px", fontWeight: 800, lineHeight: 1.3, marginBottom: "10px", color: "#ffffff" }}>
              Secure Your Browsing
              <br />
              With AI-Powered Protection
            </h3>
            <p style={{ fontSize: "13px", color: "rgba(255, 255, 255, 0.78)", lineHeight: 1.55, marginBottom: "22px" }}>
              Detect zero-day phishing links, homoglyph lookalikes, and active threat feeds before clicking.
            </p>

            <div
              style={{
                background: "rgba(255, 255, 255, 0.08)",
                border: "1px solid rgba(255, 255, 255, 0.16)",
                borderRadius: "16px",
                padding: "16px 20px",
                display: "inline-flex",
                flexDirection: "column",
                alignItems: "center",
              }}
            >
              <LaptopShieldArtwork />
              <div style={{ fontSize: "12px", color: "#e0e7ff", fontWeight: 600, marginTop: "6px" }}>
                Real-Time LightGBM + Threat Intel
              </div>
            </div>
          </div>

          <div style={{ fontSize: "11px", color: "rgba(255, 255, 255, 0.65)" }}>
            Argon2 Password Hashing • HMAC-SHA256 Sessions
          </div>
        </div>

        {/* Right Form Panel (Board 11) */}
        <div className="split-auth-form">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
            <div className="auth-tabs" style={{ margin: 0, flex: 1 }}>
              <button
                type="button"
                className={`auth-tab-btn ${mode === "login" ? "active" : ""}`}
                onClick={() => {
                  setMode("login");
                  setError(null);
                  setInfoNotice(null);
                }}
              >
                Login
              </button>
              <button
                type="button"
                className={`auth-tab-btn ${mode === "register" ? "active" : ""}`}
                onClick={() => {
                  setMode("register");
                  setError(null);
                  setInfoNotice(null);
                }}
              >
                Register
              </button>
            </div>

            <button
              type="button"
              onClick={onClose}
              aria-label="Close authentication modal"
              style={{
                background: "none",
                border: "none",
                color: "var(--text-muted)",
                cursor: "pointer",
                width: "36px",
                height: "36px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                borderRadius: "8px",
                marginLeft: "8px",
              }}
            >
              <CloseIcon size={18} />
            </button>
          </div>

          {error && (
            <div className="state-card-error" style={{ padding: "10px 14px", marginTop: "14px", fontSize: "13px", textAlign: "left" }}>
              {error}
            </div>
          )}

          {infoNotice && (
            <div
              style={{
                background: "#eff6ff",
                border: "1px solid #bfdbfe",
                color: "#1d4ed8",
                borderRadius: "10px",
                padding: "10px 14px",
                marginTop: "14px",
                fontSize: "12px",
              }}
            >
              {infoNotice}
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ marginTop: "18px" }}>
            {mode === "register" && (
              <div className="form-group">
                <label className="form-label" htmlFor="auth-fullname">Full Name</label>
                <input
                  id="auth-fullname"
                  type="text"
                  className="form-input"
                  placeholder="John Doe"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  required
                />
              </div>
            )}

            <div className="form-group">
              <label className="form-label" htmlFor="auth-email">Email Address</label>
              <input
                id="auth-email"
                type="email"
                className="form-input"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="auth-password">Password</label>
              <div style={{ position: "relative" }}>
                <input
                  id="auth-password"
                  type={showPassword ? "text" : "password"}
                  className="form-input"
                  style={{ paddingRight: "48px" }}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  style={{
                    position: "absolute",
                    right: "8px",
                    top: "50%",
                    transform: "translateY(-50%)",
                    background: "none",
                    border: "none",
                    cursor: "pointer",
                    fontSize: "12px",
                    fontWeight: 600,
                    color: "var(--color-primary)",
                    padding: "6px",
                  }}
                >
                  {showPassword ? "Hide" : "Show"}
                </button>
              </div>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "12px", marginBottom: "18px", gap: "8px", flexWrap: "wrap" }}>
              <label style={{ display: "flex", alignItems: "center", gap: "6px", cursor: "pointer", color: "var(--text-secondary)" }}>
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                />
                Remember me
              </label>
              <button
                type="button"
                onClick={() => setInfoNotice("Password recovery can be updated inside Account Settings once signed in.")}
                style={{ background: "none", border: "none", color: "var(--color-primary)", fontSize: "12px", fontWeight: 600, cursor: "pointer" }}
              >
                Forgot password?
              </button>
            </div>

            <button type="submit" className="btn-primary" style={{ width: "100%", minHeight: "46px", fontSize: "15px" }} disabled={loading}>
              {loading ? "Authenticating..." : mode === "login" ? "Login" : "Create Account"}
            </button>
          </form>

          <div style={{ marginTop: "20px", textAlign: "center" }}>
            <div style={{ fontSize: "12px", color: "var(--text-muted)", marginBottom: "10px" }}>
              Or continue with
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
              <button
                type="button"
                className="filter-pill"
                style={{ justifyContent: "center", minHeight: "40px" }}
                onClick={() => setInfoNotice("Local backend uses JWT Email + Password login. Please sign in or register above.")}
              >
                <span style={{ fontWeight: 700, color: "#ea4335" }}>G</span> Google
              </button>
              <button
                type="button"
                className="filter-pill"
                style={{ justifyContent: "center", minHeight: "40px" }}
                onClick={() => setInfoNotice("Local backend uses JWT Email + Password login. Please sign in or register above.")}
              >
                <span style={{ fontWeight: 700, color: "#0f172a" }}>GH</span> GitHub
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
