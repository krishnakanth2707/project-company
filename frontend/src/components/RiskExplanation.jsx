const RISK_COLORS = {
  "Very Low":"#065f46","Low":"#1e40af","Medium":"#92400e","High":"#9a3412","Very High":"#991b1b"
};

export default function RiskExplanation({ text, probabilities }) {
  return (
    <div style={{ background: "#f8fafc", borderRadius: 12, padding: 20, border: "1px solid #e2e8f0" }}>
      <div style={{ fontWeight: 600, marginBottom: 8, color: "#1e293b" }}>🔍 Risk Explanation</div>
      <p style={{ fontSize: 14, color: "#475569", lineHeight: 1.6, margin: "0 0 12px" }}>{text}</p>
      {Object.entries(probabilities).map(([k, v]) => (
        <div key={k} style={{ marginBottom: 4 }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 2 }}>
            <span>{k}</span><span>{(v * 100).toFixed(1)}%</span>
          </div>
          <div style={{ height: 6, background: "#e2e8f0", borderRadius: 3 }}>
            <div style={{ height: "100%", width: `${v*100}%`, background: RISK_COLORS[k] || "#888", borderRadius: 3 }}/>
          </div>
        </div>
      ))}
    </div>
  );
}