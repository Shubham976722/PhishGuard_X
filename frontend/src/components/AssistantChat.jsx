import React, { useEffect, useRef, useState } from "react";
import { askAboutScan, askAssistant } from "../services/api";
import { getScanDisplayMetrics } from "../utils/scanHelpers";
import { AssistantIcon, SendIcon } from "./Icons";

export function AssistantChat({ user, onRequireAuth, initialScan }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (initialScan) {
      const { riskPct, isSafe } = getScanDisplayMetrics(initialScan);
      const sourceText = initialScan.threat_sources?.length
        ? `It appears in verified threat intelligence feeds (${initialScan.threat_sources.join(", ")})`
        : "Our lexical feature extractor analyzed its hostname, protocol, and token patterns";

      setMessages([
        {
          role: "user",
          content: `Why was this URL classified this way: ${initialScan.url}?`,
        },
        {
          role: "assistant",
          content: `This URL recorded a phishing risk score of ${riskPct}%:\n\n• ${sourceText}\n• ${
            isSafe
              ? "Model and feed checks indicate low malicious risk."
              : "Our LightGBM classifier flagged elevated phishing risk characteristics."
          }\n• Ask any follow-up question below to explore the indicators further.`,
          sources: initialScan.threat_sources?.length ? initialScan.threat_sources : ["ML Analysis"],
        },
      ]);
    } else {
      setMessages([
        {
          role: "assistant",
          content:
            "Hello! I am your AI Cybersecurity Assistant. Ask me anything about phishing techniques, domain safety, or a specific URL inspection result.",
          sources: ["phishing_fundamentals.md"],
        },
      ]);
    }
  }, [initialScan]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async (questionText) => {
    const q = (questionText || input).trim();
    if (!q || loading) return;

    if (!user) {
      onRequireAuth();
      return;
    }

    setMessages((prev) => [...prev, { role: "user", content: q }]);
    if (!questionText) setInput("");
    setLoading(true);

    try {
      const data = initialScan?.id
        ? await askAboutScan(initialScan.id, q)
        : await askAssistant(q);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer || "I processed your inquiry based on verified cybersecurity guidance.",
          sources: data.sources || [],
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Unable to complete AI inquiry: ${err.message}. Please verify the backend and local LLM service are running.`,
          isError: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-shell">
      {/* Chat Header (Board 7) */}
      <div
        className="stat-card"
        style={{
          marginBottom: "12px",
          padding: "14px 18px",
          flexDirection: "row",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "10px",
        }}
      >
        <div>
          <h2 style={{ fontSize: "17px", fontWeight: 800, margin: 0 }}>AI Security Assistant</h2>
          <span style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
            Grounded cybersecurity & phishing Q&A
          </span>
        </div>

        {initialScan?.url && (
          <span
            style={{
              background: "#eff6ff",
              color: "var(--color-primary)",
              border: "1px solid #bfdbfe",
              borderRadius: "9999px",
              padding: "4px 12px",
              fontSize: "11px",
              fontFamily: "var(--font-mono)",
              fontWeight: 600,
              maxWidth: "100%",
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
            title={initialScan.url}
          >
            Context: {initialScan.url}
          </span>
        )}
      </div>

      {/* Quick Inquiry Chips */}
      <div className="chat-chips-row">
        {[
          "Why was this URL flagged?",
          "How to spot homograph domains?",
          "What is Punycode obfuscation?",
          "How do threat feeds detect malware?",
        ].map((chip) => (
          <button
            key={chip}
            type="button"
            onClick={() => handleSend(chip)}
            className="filter-pill"
            style={{ fontSize: "12px" }}
          >
            {chip}
          </button>
        ))}
      </div>

      {/* Message Thread */}
      <div className="stat-card chat-thread">
        {messages.map((m, idx) => {
          const isUser = m.role === "user";
          return (
            <div
              key={idx}
              style={{
                display: "flex",
                justifyContent: isUser ? "flex-end" : "flex-start",
                alignItems: "flex-start",
                gap: "10px",
                minWidth: 0,
              }}
            >
              {!isUser && (
                <div
                  style={{
                    width: "34px",
                    height: "34px",
                    borderRadius: "10px",
                    background: "rgba(99, 102, 241, 0.12)",
                    color: "var(--color-purple-dark)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexShrink: 0,
                  }}
                >
                  <AssistantIcon size={18} />
                </div>
              )}

              <div
                style={{
                  maxWidth: "min(88%, 620px)",
                  minWidth: 0,
                  background: isUser ? "var(--gradient-brand)" : m.isError ? "var(--danger-bg)" : "#f8fafc",
                  color: isUser ? "#ffffff" : m.isError ? "var(--danger-red-dark)" : "var(--text-primary)",
                  border: isUser ? "none" : `1px solid ${m.isError ? "var(--danger-border)" : "var(--card-border)"}`,
                  borderRadius: isUser ? "14px 14px 4px 14px" : "14px 14px 14px 4px",
                  padding: "12px 16px",
                  fontSize: "14px",
                  lineHeight: 1.58,
                  boxShadow: "var(--card-shadow)",
                  wordBreak: "break-word",
                  overflowWrap: "anywhere",
                }}
              >
                <div style={{ whiteSpace: "pre-wrap" }}>{m.content}</div>

                {m.sources && m.sources.length > 0 && (
                  <div
                    style={{
                      marginTop: "10px",
                      paddingTop: "8px",
                      borderTop: "1px solid rgba(15, 23, 42, 0.08)",
                      fontSize: "11px",
                      color: isUser ? "rgba(255,255,255,0.85)" : "var(--text-secondary)",
                    }}
                  >
                    <strong>Sources:</strong> {m.sources.join(", ")}
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {loading && (
          <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
            <div
              style={{
                width: "34px",
                height: "34px",
                borderRadius: "10px",
                background: "rgba(99, 102, 241, 0.12)",
                color: "var(--color-purple-dark)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
              }}
            >
              <AssistantIcon size={18} />
            </div>
            <div
              style={{
                background: "#f8fafc",
                border: "1px solid var(--card-border)",
                padding: "12px 16px",
                borderRadius: "14px",
                fontSize: "13px",
                color: "var(--text-secondary)",
              }}
            >
              Retrieving grounded security documents & synthesizing answer...
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Bottom Input Field */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        style={{ display: "flex", gap: "10px", marginTop: "12px" }}
      >
        <input
          type="text"
          className="scan-text-input"
          placeholder="Ask a cybersecurity question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
          aria-label="Ask AI security assistant"
        />
        <button
          type="submit"
          className="btn-primary"
          disabled={loading || !input.trim()}
          aria-label="Send question"
          style={{ minWidth: "48px", minHeight: "44px", padding: "10px 18px" }}
        >
          <SendIcon size={18} />
        </button>
      </form>
    </div>
  );
}
