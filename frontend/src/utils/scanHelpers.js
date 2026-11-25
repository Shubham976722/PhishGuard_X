/**
 * Shared scan formatting, TreeSHAP explanation parsing, and telemetry aggregation helpers.
 */

export function getScanDisplayMetrics(scan) {
  const verdict = (scan?.verdict || "legitimate").toLowerCase();
  const isPhish = verdict === "phishing" || verdict === "malware";
  const isSuspicious = verdict === "suspicious" || verdict === "unknown";
  const isSafe = !isPhish && !isSuspicious;

  const rawScore = scan?.risk_score != null ? Number(scan.risk_score) : isSafe ? 5 : 85;
  const riskPct = rawScore > 1 ? rawScore : rawScore * 100;
  const clampedRisk = Math.max(0, Math.min(100, riskPct));

  const confidenceValue = isSafe
    ? Math.max(0, Math.min(100, 100 - clampedRisk))
    : clampedRisk;

  const statusKey = isSafe ? "safe" : isPhish ? "danger" : "warn";
  const statusLabel = isSafe
    ? "Safe"
    : verdict === "malware"
      ? "Malware"
      : isPhish
        ? "Phishing"
        : "Unknown";

  return {
    isPhish,
    isSuspicious,
    isSafe,
    statusKey,
    statusLabel,
    riskPct: Number(clampedRisk.toFixed(1)),
    confidence: confidenceValue.toFixed(1),
    confidenceNumber: Number(confidenceValue.toFixed(1)),
  };
}

export function parseScanExplanation(explanationText) {
  if (!explanationText || typeof explanationText !== "string") {
    return {
      modelName: "LightGBM Classifier",
      probabilityText: null,
      factors: [],
      threatSummary: null,
    };
  }

  const lines = explanationText.split(/\r?\n/);
  let modelName = "LightGBM Classifier";
  let probabilityText = null;
  let threatSummary = null;
  const factors = [];

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line) continue;

    if (line.startsWith("Model:")) {
      modelName = line.replace("Model:", "").trim() || modelName;
      continue;
    }

    if (line.startsWith("Phishing probability:")) {
      probabilityText = line.replace("Phishing probability:", "").trim();
      continue;
    }

    if (line.startsWith("Threat intelligence:")) {
      threatSummary = line.replace("Threat intelligence:", "").trim();
      continue;
    }

    // Parse lines like: "- Suspicious keywords: increases phishing risk (contribution: 1.24)"
    const factorMatch = line.match(/^-\s+([^:]+):\s+(.+?)\s*\(contribution:\s*([-+]?\d*\.?\d+)\)$/i);
    if (factorMatch) {
      const feature = factorMatch[1].trim();
      const impactText = factorMatch[2].trim();
      const contribution = Number(factorMatch[3]);
      factors.push({
        feature,
        impactText,
        contribution: Number.isFinite(contribution) ? contribution : 0,
        increasesRisk: contribution > 0 || impactText.toLowerCase().includes("increase"),
        decreasesRisk: contribution < 0 || impactText.toLowerCase().includes("decrease"),
      });
    }
  }

  return {
    modelName,
    probabilityText,
    factors,
    threatSummary,
  };
}

export function filterScansByTimeRange(scans, timeRange) {
  if (!Array.isArray(scans)) return [];
  if (timeRange === "all") return scans;

  const days = timeRange === "7d" ? 7 : 30;
  const cutoff = Date.now() - days * 24 * 60 * 60 * 1000;

  return scans.filter((scan) => {
    if (!scan?.scanned_at) return true;
    const ts = Date.parse(scan.scanned_at);
    return Number.isNaN(ts) ? true : ts >= cutoff;
  });
}

export function formatScanDate(isoString, includeTime = false) {
  if (!isoString) return "Recently";
  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) return "Recently";

  if (includeTime) {
    return date.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

/**
 * Builds a 7-day rolling series from scan records for the Dashboard SVG chart.
 */
export function buildWeeklyActivitySeries(scans) {
  const days = [];
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  for (let offset = 6; offset >= 0; offset--) {
    const d = new Date(today);
    d.setDate(today.getDate() - offset);
    const key = d.toISOString().slice(0, 10);
    const label = d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
    days.push({ key, label, safe: 0, phishing: 0, unknown: 0, total: 0 });
  }

  const byKey = Object.fromEntries(days.map((item) => [item.key, item]));

  if (Array.isArray(scans)) {
    for (const scan of scans) {
      if (!scan?.scanned_at) continue;
      const parsed = new Date(scan.scanned_at);
      if (Number.isNaN(parsed.getTime())) continue;
      const key = parsed.toISOString().slice(0, 10);
      const bucket = byKey[key];
      if (!bucket) continue;

      const { isSafe, isPhish } = getScanDisplayMetrics(scan);
      if (isSafe) bucket.safe += 1;
      else if (isPhish) bucket.phishing += 1;
      else bucket.unknown += 1;
      bucket.total += 1;
    }
  }

  return days;
}
