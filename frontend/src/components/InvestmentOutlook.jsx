export default function InvestmentOutlook({ text, headlines }) {
  return (
    <div style={{ background: "#f8fafc", borderRadius: 12, padding: 20, border: "1px solid #e2e8f0" }}>
      <div style={{ fontWeight: 600, marginBottom: 8, color: "#1e293b" }}>💡 Investment Outlook</div>
      <p style={{ fontSize: 14, color: "#475569", lineHeight: 1.6, margin: "0 0 12px" }}>{text}</p>
      <div style={{ fontWeight: 500, fontSize: 12, color: "#64748b", marginBottom: 6 }}>Recent News</div>
      {headlines.map((h, i) => (
        <div key={i} style={{ fontSize: 12, color: "#475569", marginBottom: 4, paddingLeft: 8,
          borderLeft: "2px solid #cbd5e1" }}>
          {h}
        </div>
      ))}
    </div>
  );
}