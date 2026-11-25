import React, { useEffect, useState } from "react";
import { getScanHistory } from "../services/api";
import {
  filterScansByTimeRange,
  formatScanDate,
  getScanDisplayMetrics,
} from "../utils/scanHelpers";
import { LockIcon } from "./Icons";

const PAGE_SIZE = 8;

export function ScanHistory({ user, onRequireAuth, onSelectScan }) {
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("all");
  const [timeRange, setTimeRange] = useState("30d");
  const [page, setPage] = useState(1);

  useEffect(() => {
    if (!user) return;
    setLoading(true);
    getScanHistory(100, 0)
      .then((data) => setScans(Array.isArray(data) ? data : []))
      .catch((err) => setError(err.message || "Failed to load scan history."))
      .finally(() => setLoading(false));
  }, [user]);

  useEffect(() => {
    setPage(1);
  }, [search, filter, timeRange]);

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
          Please sign in to access your historical scan timeline, filter verdicts, and inspect threat breakdowns.
        </p>
        <button type="button" onClick={onRequireAuth} className="btn-primary" style={{ padding: "10px 24px" }}>
          Sign In to View History
        </button>
      </div>
    );
  }

  // Filter by time range, search query, and verdict pill
  const timeFiltered = filterScansByTimeRange(scans, timeRange);
  const filtered = timeFiltered.filter((s) => {
    const matchesSearch = !search || s.url.toLowerCase().includes(search.toLowerCase());
    if (!matchesSearch) return false;

    const { isSafe, isPhish } = getScanDisplayMetrics(s);
    if (filter === "all") return true;
    if (filter === "safe") return isSafe;
    if (filter === "phishing") return isPhish;
    if (filter === "unknown") return !isSafe && !isPhish;
    return true;
  });

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const safePage = Math.min(page, totalPages);
  const startIndex = (safePage - 1) * PAGE_SIZE;
  const pagedScans = filtered.slice(startIndex, startIndex + PAGE_SIZE);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "18px" }}>
      {/* Top Filter & Search Controls (Board 5) */}
      <div className="filter-row">
        <div className="pill-group" role="tablist" aria-label="Verdict filter">
          {[
            { id: "all", label: "All" },
            { id: "safe", label: "✓ Safe" },
            { id: "phishing", label: "! Phishing" },
            { id: "unknown", label: "Unknown" },
          ].map((item) => (
            <button
              key={item.id}
              type="button"
              className={`filter-pill ${filter === item.id ? "active" : ""}`}
              onClick={() => setFilter(item.id)}
            >
              {item.label}
            </button>
          ))}
        </div>

        <div style={{ display: "flex", gap: "10px", alignItems: "center", flexWrap: "wrap", flex: "1 1 260px", justifyContent: "flex-end" }}>
          <input
            type="search"
            className="scan-text-input"
            style={{ minWidth: "160px", maxWidth: "300px", padding: "8px 14px", fontSize: "13px" }}
            placeholder="Search URLs..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Search scan history by URL"
          />

          <select
            className="scan-text-input"
            style={{ width: "auto", flex: "0 0 auto", padding: "8px 12px", fontSize: "13px", cursor: "pointer" }}
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            aria-label="Filter by date range"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="all">All time</option>
          </select>
        </div>
      </div>

      {error && (
        <div className="state-card-error" style={{ padding: "18px" }}>
          {error}
        </div>
      )}

      {/* History Card: Desktop/Tablet Table + Mobile Card View */}
      <div className="stat-card" style={{ padding: 0, overflow: "hidden" }}>
        {loading ? (
          <div style={{ padding: "44px 20px", textAlign: "center" }}>
            <div className="spinner-circle" />
            <p style={{ color: "var(--text-secondary)", fontSize: "14px" }}>Loading scan history...</p>
          </div>
        ) : filtered.length === 0 ? (
          <div style={{ padding: "56px 20px", textAlign: "center", color: "var(--text-secondary)", fontSize: "14px" }}>
            No scan records found matching your filter criteria.
          </div>
        ) : (
          <>
            {/* Tablet & Desktop Table (Board 5) */}
            <div className="history-table-wrap table-responsive">
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "14px", minWidth: "540px" }}>
                <thead>
                  <tr style={{ background: "#f8fafc", borderBottom: "1px solid var(--card-border)", textAlign: "left" }}>
                    <th style={{ padding: "14px 20px", color: "var(--text-secondary)", fontWeight: 600, fontSize: "13px" }}>URL</th>
                    <th style={{ padding: "14px 20px", color: "var(--text-secondary)", fontWeight: 600, fontSize: "13px" }}>Result</th>
                    <th style={{ padding: "14px 20px", color: "var(--text-secondary)", fontWeight: 600, fontSize: "13px" }}>Confidence</th>
                    <th style={{ padding: "14px 20px", color: "var(--text-secondary)", fontWeight: 600, fontSize: "13px" }}>Date</th>
                  </tr>
                </thead>
                <tbody>
                  {pagedScans.map((s) => {
                    const { statusKey, statusLabel, confidence } = getScanDisplayMetrics(s);
                    const pillClass =
                      statusKey === "safe"
                        ? "badge-pill-safe"
                        : statusKey === "danger"
                          ? "badge-pill-danger"
                          : "badge-pill-warn";

                    return (
                      <tr
                        key={s.id}
                        onClick={() => onSelectScan(s)}
                        style={{ borderBottom: "1px solid var(--card-border)", cursor: "pointer", transition: "background-color 0.12s" }}
                        onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#f8fafc")}
                        onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "transparent")}
                      >
                        <td
                          style={{
                            padding: "14px 20px",
                            maxWidth: "320px",
                            overflow: "hidden",
                            textOverflow: "ellipsis",
                            whiteSpace: "nowrap",
                            color: "var(--text-primary)",
                            fontWeight: 500,
                            fontFamily: "var(--font-mono)",
                            fontSize: "13px",
                          }}
                        >
                          {s.url}
                        </td>
                        <td style={{ padding: "14px 20px", whiteSpace: "nowrap" }}>
                          <span className={pillClass}>{statusLabel}</span>
                        </td>
                        <td style={{ padding: "14px 20px", color: "var(--text-primary)", fontWeight: 700, whiteSpace: "nowrap" }}>
                          {confidence}%
                        </td>
                        <td style={{ padding: "14px 20px", color: "var(--text-secondary)", fontSize: "13px", whiteSpace: "nowrap" }}>
                          {formatScanDate(s.scanned_at)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Mobile Card Layout (Visible <= 640px) */}
            <div className="history-mobile-list">
              {pagedScans.map((s) => {
                const { statusKey, statusLabel, confidence } = getScanDisplayMetrics(s);
                const pillClass =
                  statusKey === "safe"
                    ? "badge-pill-safe"
                    : statusKey === "danger"
                      ? "badge-pill-danger"
                      : "badge-pill-warn";

                return (
                  <div key={s.id} className="history-mobile-card" onClick={() => onSelectScan(s)}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "8px" }}>
                      <span className={pillClass}>{statusLabel}</span>
                      <span style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
                        {formatScanDate(s.scanned_at)}
                      </span>
                    </div>

                    <div
                      style={{
                        fontFamily: "var(--font-mono)",
                        fontSize: "13px",
                        fontWeight: 600,
                        color: "var(--text-primary)",
                        wordBreak: "break-all",
                      }}
                    >
                      {s.url}
                    </div>

                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "12px" }}>
                      <span style={{ color: "var(--text-secondary)" }}>
                        Confidence: <strong style={{ color: "var(--text-primary)" }}>{confidence}%</strong>
                      </span>
                      <span style={{ color: "var(--color-primary)", fontWeight: 600 }}>View Details →</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </>
        )}

        {/* Working Pagination Footer (Board 5) */}
        {!loading && filtered.length > 0 && (
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              flexWrap: "wrap",
              gap: "10px",
              padding: "14px 18px",
              background: "#ffffff",
            }}
          >
            <span style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
              Showing {startIndex + 1}–{Math.min(startIndex + PAGE_SIZE, filtered.length)} of {filtered.length} scans
            </span>

            <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
              <button
                type="button"
                className="filter-pill"
                style={{ padding: "5px 11px", fontSize: "12px", opacity: safePage <= 1 ? 0.45 : 1 }}
                disabled={safePage <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                aria-label="Previous page"
              >
                &lt;
              </button>

              {Array.from({ length: totalPages }, (_, idx) => idx + 1).map((pageNum) => (
                <button
                  key={pageNum}
                  type="button"
                  className={`filter-pill ${safePage === pageNum ? "active" : ""}`}
                  style={{ padding: "5px 11px", fontSize: "12px" }}
                  onClick={() => setPage(pageNum)}
                >
                  {pageNum}
                </button>
              ))}

              <button
                type="button"
                className="filter-pill"
                style={{ padding: "5px 11px", fontSize: "12px", opacity: safePage >= totalPages ? 0.45 : 1 }}
                disabled={safePage >= totalPages}
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                aria-label="Next page"
              >
                &gt;
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
