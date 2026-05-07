import { useState } from "react";
const PERIODS = ["1M","3M","6M","1Y","3Y","5Y"];

export default function TickerForm({ onSubmit, loading }) {
  const [ticker, setTicker] = useState("AAPL");
  const [period, setPeriod] = useState("1Y");

  return (
    <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
      <input
        value={ticker}
        onChange={e => setTicker(e.target.value.toUpperCase())}
        placeholder="Ticker e.g. AAPL"
        style={{ padding: "10px 14px", borderRadius: 8, border: "1px solid #d1d5db", fontSize: 15, width: 160 }}
      />
      <div style={{ display: "flex", gap: 6 }}>
        {PERIODS.map(p => (
          <button key={p} onClick={() => setPeriod(p)}
            style={{ padding: "10px 14px", borderRadius: 8, border: "1px solid #d1d5db",
              background: period === p ? "#2563eb" : "#fff",
              color: period === p ? "#fff" : "#374151", cursor: "pointer", fontWeight: 500 }}>
            {p}
          </button>
        ))}
      </div>
      <button onClick={() => onSubmit({ ticker, period })} disabled={loading}
        style={{ padding: "10px 24px", borderRadius: 8, background: loading ? "#93c5fd" : "#2563eb",
          color: "#fff", border: "none", cursor: loading ? "not-allowed" : "pointer", fontWeight: 600, fontSize: 15 }}>
        {loading ? "Analysing…" : "Analyse Risk"}
      </button>
    </div>
  );
}