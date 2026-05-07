export default function MarketSummary({ text, features }) {
  return (
    <div style={{ background: "#f8fafc", borderRadius: 12, padding: 20, border: "1px solid #e2e8f0" }}>
      <div style={{ fontWeight: 600, marginBottom: 8, color: "#1e293b" }}>📊 Market Summary</div>
      <p style={{ fontSize: 14, color: "#475569", lineHeight: 1.6, margin: 0 }}>{text}</p>
      <div style={{ marginTop: 12, fontSize: 13 }}>
        <div>ROI: <b style={{ color: features.roi >= 0 ? "green" : "red" }}>{features.roi?.toFixed(2)}%</b></div>
        <div>Volatility: <b>{features.volatility?.toFixed(2)}%</b></div>
        <div>RSI: <b>{features.rsi?.toFixed(1)}</b></div>
      </div>
    </div>
  );
}