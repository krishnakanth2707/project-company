const COLORS = {
  "Very Low":  { bg: "#d1fae5", color: "#065f46" },
  "Low":       { bg: "#dbeafe", color: "#1e40af" },
  "Medium":    { bg: "#fef3c7", color: "#92400e" },
  "High":      { bg: "#fed7aa", color: "#9a3412" },
  "Very High": { bg: "#fee2e2", color: "#991b1b" },
};

export default function RiskBadge({ label, confidence }) {
  const c = COLORS[label] || COLORS["Medium"];
  return (
    <div style={{ ...c, padding: "12px 20px", borderRadius: 12, fontWeight: 700,
      fontSize: 18, display: "inline-block", marginLeft: "auto" }}>
      {label} Risk
      <div style={{ fontSize: 12, fontWeight: 400, marginTop: 2 }}>
        Confidence: {(confidence * 100).toFixed(1)}%
      </div>
    </div>
  );
}