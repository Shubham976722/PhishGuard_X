import React from "react";

export function BrandShieldIcon({ size = 20 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M12 2.5L19.5 5.6C19.5 11.9 16.3 17.5 12 20.8C7.7 17.5 4.5 11.9 4.5 5.6L12 2.5Z"
        fill="currentColor"
        fillOpacity="0.18"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinejoin="round"
      />
      <path
        d="M9.2 11.8L11.1 13.7L15 9.6"
        stroke="currentColor"
        strokeWidth="2.1"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function HeroShieldArtwork() {
  return (
    <svg
      viewBox="0 0 360 320"
      className="hero-shield-svg"
      role="img"
      aria-label="PhishGuard X AI Security Shield"
    >
      <defs>
        <linearGradient id="pgHeroBgGlow" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#60a5fa" stopOpacity="0.28" />
          <stop offset="50%" stopColor="#6366f1" stopOpacity="0.2" />
          <stop offset="100%" stopColor="#a855f7" stopOpacity="0.12" />
        </linearGradient>
        <linearGradient id="pgShieldOuter" x1="0.1" y1="0" x2="0.9" y2="1">
          <stop offset="0%" stopColor="#3b82f6" />
          <stop offset="50%" stopColor="#4f46e5" />
          <stop offset="100%" stopColor="#7c3aed" />
        </linearGradient>
        <linearGradient id="pgShieldInner" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#93c5fd" stopOpacity="0.9" />
          <stop offset="100%" stopColor="#e0e7ff" stopOpacity="0.35" />
        </linearGradient>
        <linearGradient id="pgOrbitStroke" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#38bdf8" />
          <stop offset="50%" stopColor="#818cf8" />
          <stop offset="100%" stopColor="#c084fc" stopOpacity="0.3" />
        </linearGradient>
        <filter id="pgSoftShadow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="16" stdDeviation="16" floodColor="#4338ca" floodOpacity="0.28" />
        </filter>
      </defs>

      {/* Ambient Aura */}
      <circle cx="180" cy="156" r="126" fill="url(#pgHeroBgGlow)" />
      <circle cx="180" cy="156" r="94" stroke="#c7d2fe" strokeWidth="1" strokeDasharray="5 6" fill="none" />

      {/* Orbital Rings (Matching Reference Storyboard) */}
      <ellipse
        cx="180"
        cy="158"
        rx="142"
        ry="54"
        transform="rotate(-24 180 158)"
        fill="none"
        stroke="url(#pgOrbitStroke)"
        strokeWidth="2.4"
      />
      <ellipse
        cx="180"
        cy="158"
        rx="136"
        ry="48"
        transform="rotate(24 180 158)"
        fill="none"
        stroke="#93c5fd"
        strokeOpacity="0.65"
        strokeWidth="1.8"
      />

      {/* Orbital Satellite Nodes */}
      <circle cx="62" cy="196" r="6" fill="#38bdf8" />
      <circle cx="298" cy="118" r="7" fill="#6366f1" />
      <circle cx="286" cy="214" r="5" fill="#10b981" />

      {/* Main 3D-Styled Shield */}
      <g filter="url(#pgSoftShadow)">
        <path
          d="M180 42L264 76C264 156 232 218 180 256C128 218 96 156 96 76L180 42Z"
          fill="url(#pgShieldOuter)"
        />
        <path
          d="M180 54L250 83C250 153 222 206 180 241C138 206 110 153 110 83L180 54Z"
          fill="none"
          stroke="url(#pgShieldInner)"
          strokeWidth="2"
        />
        {/* Subtle Glass Highlight */}
        <path
          d="M180 48L114 78C114 118 122 152 138 182C154 134 184 96 242 74L180 48Z"
          fill="#ffffff"
          fillOpacity="0.14"
        />
      </g>

      {/* Central Lock Emblem inside Shield */}
      <g transform="translate(152, 114)">
        <path
          d="M14 24V16C14 8.3 20.3 2 28 2C35.7 2 42 8.3 42 16V24"
          fill="none"
          stroke="#ffffff"
          strokeWidth="5.5"
          strokeLinecap="round"
        />
        <rect x="4" y="24" width="48" height="38" rx="10" fill="#ffffff" />
        <circle cx="28" cy="40" r="4.5" fill="#4f46e5" />
        <rect x="26" y="42" width="4" height="9" rx="2" fill="#4f46e5" />
      </g>
    </svg>
  );
}

export function LaptopShieldArtwork() {
  return (
    <svg viewBox="0 0 220 150" width="180" height="122" fill="none" aria-hidden="true">
      <defs>
        <linearGradient id="pgLaptopScreen" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#312e81" />
          <stop offset="100%" stopColor="#1e3a8a" />
        </linearGradient>
        <linearGradient id="pgLaptopShield" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#60a5fa" />
          <stop offset="100%" stopColor="#6366f1" />
        </linearGradient>
      </defs>
      {/* Screen */}
      <rect x="34" y="16" width="152" height="96" rx="10" fill="url(#pgLaptopScreen)" stroke="#818cf8" strokeOpacity="0.55" strokeWidth="2" />
      <rect x="44" y="26" width="132" height="76" rx="5" fill="#0f172a" fillOpacity="0.55" />
      {/* Base */}
      <path d="M16 116H204L194 130H26L16 116Z" fill="#cbd5e1" fillOpacity="0.88" />
      <rect x="88" y="119" width="44" height="3" rx="1.5" fill="#64748b" />
      {/* Shield Overlay */}
      <path
        d="M110 38L138 50C138 74 126 92 110 102C94 92 82 74 82 50L110 38Z"
        fill="url(#pgLaptopShield)"
        stroke="#e0e7ff"
        strokeWidth="2"
      />
      <path d="M100 68L107 75L121 61" stroke="#ffffff" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function DashboardIcon({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <rect x="3" y="3" width="7" height="9" rx="2" />
      <rect x="14" y="3" width="7" height="5" rx="2" />
      <rect x="14" y="12" width="7" height="9" rx="2" />
      <rect x="3" y="16" width="7" height="5" rx="2" />
    </svg>
  );
}

export function ScannerIcon({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <circle cx="11" cy="11" r="7" />
      <path d="M20 20L16.2 16.2" />
      <path d="M8.5 11L10.3 12.8L13.8 9.2" />
    </svg>
  );
}

export function HistoryIcon({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <circle cx="12" cy="12" r="9" />
      <polyline points="12 7 12 12 15.5 14" />
    </svg>
  );
}

export function ReportsIcon({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M14 2H7a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7z" />
      <polyline points="14 2 14 7 19 7" />
      <line x1="9" y1="13" x2="15" y2="13" />
      <line x1="9" y1="17" x2="13" y2="17" />
    </svg>
  );
}

export function AssistantIcon({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <rect x="4" y="7" width="16" height="12" rx="4" />
      <path d="M12 3V7" />
      <circle cx="9.5" cy="13" r="1.2" fill="currentColor" stroke="none" />
      <circle cx="14.5" cy="13" r="1.2" fill="currentColor" stroke="none" />
      <path d="M2 13H4" />
      <path d="M20 13H22" />
    </svg>
  );
}

export function SettingsIcon({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9c.26.6.79 1 1.51 1H21a2 2 0 1 1 0 4h-.09c-.72 0-1.25.4-1.51 1z" />
    </svg>
  );
}

export function LogoutIcon({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
      <polyline points="16 17 21 12 16 7" />
      <line x1="21" y1="12" x2="9" y2="12" />
    </svg>
  );
}

export function BellIcon({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9" />
      <path d="M13.73 21a2 2 0 0 1-3.46 0" />
    </svg>
  );
}

export function MenuIcon({ size = 20 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" aria-hidden="true">
      <line x1="4" y1="7" x2="20" y2="7" />
      <line x1="4" y1="12" x2="20" y2="12" />
      <line x1="4" y1="17" x2="20" y2="17" />
    </svg>
  );
}

export function CloseIcon({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" aria-hidden="true">
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}

export function DownloadIcon({ size = 16 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="7 10 12 15 17 10" />
      <line x1="12" y1="15" x2="12" y2="3" />
    </svg>
  );
}

export function PuzzleIcon({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M19.439 7.85c0-1.1-.9-2-2-2H14V4.5a2.5 2.5 0 0 0-5 0V5.85H5.56c-1.1 0-2 .9-2 2V11h1.35a2.5 2.5 0 0 1 0 5H3.56v3.15c0 1.1.9 2 2 2H9v-1.35a2.5 2.5 0 0 1 5 0V21.15h3.44c1.1 0 2-.9 2-2V15.5h-1.35a2.5 2.5 0 0 1 0-5h1.35V7.85z" />
    </svg>
  );
}

export function SendIcon({ size = 17 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <line x1="22" y1="2" x2="11" y2="13" />
      <polygon points="22 2 15 22 11 13 2 9 22 2" />
    </svg>
  );
}

export function SparklesIcon({ size = 16 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M12 3l1.9 5.3L19 10.2l-5.1 1.9L12 17.5l-1.9-5.4L5 10.2l5.1-1.9L12 3z" />
    </svg>
  );
}

export function LightbulbIcon({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M9 18h6" />
      <path d="M10 22h4" />
      <path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1 .23 2.23 1.5 3.5A4.61 4.61 0 0 1 8.91 14" />
    </svg>
  );
}

export function ShieldCheckBadgeIcon({ size = 30 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M12 2L4 5.5v6.1c0 5.1 3.4 9.8 8 11.1 4.6-1.3 8-6 8-11.1V5.5L12 2zm-1.1 13.4l-3.4-3.4 1.4-1.4 2 2 4.6-4.6 1.4 1.4-6 6z" />
    </svg>
  );
}

export function ShieldAlertBadgeIcon({ size = 30 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M12 2L4 5.5v6.1c0 5.1 3.4 9.8 8 11.1 4.6-1.3 8-6 8-11.1V5.5L12 2zm1 13.5h-2v-2h2v2zm0-4h-2V7h2v4.5z" />
    </svg>
  );
}

export function LockIcon({ size = 20 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
      <path d="M7 11V7a5 5 0 0 1 10 0v4" />
    </svg>
  );
}
