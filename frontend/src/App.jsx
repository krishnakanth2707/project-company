import { useState } from "react";
import { analyzeStock } from "./api";
import TickerForm from "./components/TickerForm";
import RiskBadge from "./components/RiskBadge";
import MarketSummary from "./components/MarketSummary";
import RiskExplanation from "./components/RiskExplanation";
import InvestmentOutlook from "./components/InvestmentOutlook";
import Charts from "./components/Charts";

export default function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = async ({ ticker, period }) => {
    setLoading(true); setError(null); setResult(null);
    try {
      const data = await analyzeStock(ticker, period);
      setResult(data);
    } catch (e) {
      setError(e.response?.data?.detail || "Analysis failed. Try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 1100, margin: "0 auto", padding: "2rem 1rem", fontFamily: "system-ui, sans-serif" }}>
      <h1 style={{ fontSize: 28, fontWeight: 600, marginBottom: 4 }}>
        AI Stock Risk Analyzer
      </h1>
      <p style={{ color: "#666", marginBottom: 24 }}>
        Powered by Random Forest + LLM analysis with live news sentiment
      </p>

      <TickerForm onSubmit={handleAnalyze} loading={loading} />

      {error && (
        <div style={{ background: "#fee2e2", color: "#b91c1c", padding: 16, borderRadius: 8, marginTop: 16 }}>
          {error}
        </div>
      )}

      {result && (
        <>
          <div style={{ display: "flex", alignItems: "center", gap: 16, margin: "28px 0 20px" }}>
            <div>
              <div style={{ fontSize: 22, fontWeight: 600 }}>{result.company}</div>
              <div style={{ color: "#666" }}>{result.ticker} · {result.period}</div>
            </div>
            <RiskBadge label={result.prediction.risk_label} confidence={result.prediction.confidence} />
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16, marginBottom: 24 }}>
            <MarketSummary text={result.llm.market_summary} features={result.features} />
            <RiskExplanation text={result.llm.risk_explanation} probabilities={result.prediction.probabilities} />
            <InvestmentOutlook text={result.llm.investment_outlook} headlines={result.headlines} />
          </div>

          <Charts data={result.chart_data} ticker={result.ticker} />
        </>
      )}
    </div>
  );
}