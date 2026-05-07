import {
  LineChart, Line, BarChart, Bar, AreaChart, Area,
  RadarChart, Radar, PolarGrid, PolarAngleAxis,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from "recharts";

export default function Charts({ data, ticker }) {
  // Downsample for performance
  const step = Math.max(1, Math.floor(data.dates.length / 120));
  const priceData = data.dates
    .filter((_, i) => i % step === 0)
    .map((date, i) => ({
      date, price: data.prices[i * step],
      ma20: data.ma20[i * step], ma50: data.ma50[i * step]
    }));

  const volData = data.dates
    .filter((_, i) => i % step === 0)
    .map((date, i) => ({ date, volume: data.volume[i * step] }));

  // Rolling 20-day volatility
  const prices = data.prices;
  const volSeries = data.dates.map((date, i) => {
    if (i < 19) return { date, volatility: null };
    const slice = prices.slice(i - 19, i + 1);
    const rets = slice.slice(1).map((p, j) => Math.log(p / slice[j]));
    const mean = rets.reduce((a, b) => a + b, 0) / rets.length;
    const std = Math.sqrt(rets.reduce((s, r) => s + (r-mean)**2, 0) / rets.length);
    return { date, volatility: +(std * Math.sqrt(252) * 100).toFixed(2) };
  }).filter((_, i) => i % step === 0);

  const axisStyle = { fontSize: 11, fill: "#94a3b8" };

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>

      {/* Chart 1: Price + Moving Averages */}
      <div style={{ background: "#f8fafc", borderRadius: 12, padding: 20, border: "1px solid #e2e8f0" }}>
        <div style={{ fontWeight: 600, marginBottom: 12 }}>Price & Moving Averages — {ticker}</div>
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={priceData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0"/>
            <XAxis dataKey="date" tick={axisStyle} tickFormatter={d => d.slice(5)}/>
            <YAxis tick={axisStyle} domain={["auto","auto"]}/>
            <Tooltip contentStyle={{ fontSize: 12 }}/>
            <Legend/>
            <Line dataKey="price" stroke="#2563eb" dot={false} strokeWidth={2} name="Price"/>
            <Line dataKey="ma20"  stroke="#f59e0b" dot={false} strokeWidth={1.5} name="MA20" strokeDasharray="4 2"/>
            <Line dataKey="ma50"  stroke="#10b981" dot={false} strokeWidth={1.5} name="MA50" strokeDasharray="4 2"/>
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Chart 2: Volume */}
      <div style={{ background: "#f8fafc", borderRadius: 12, padding: 20, border: "1px solid #e2e8f0" }}>
        <div style={{ fontWeight: 600, marginBottom: 12 }}>Trading Volume</div>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={volData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0"/>
            <XAxis dataKey="date" tick={axisStyle} tickFormatter={d => d.slice(5)}/>
            <YAxis tick={axisStyle} tickFormatter={v => (v/1e6).toFixed(0)+'M'}/>
            <Tooltip contentStyle={{ fontSize: 12 }} formatter={v => [(v/1e6).toFixed(2)+'M', "Volume"]}/>
            <Bar dataKey="volume" fill="#6366f1" radius={[2,2,0,0]}/>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Chart 3: Rolling Volatility */}
      <div style={{ background: "#f8fafc", borderRadius: 12, padding: 20, border: "1px solid #e2e8f0" }}>
        <div style={{ fontWeight: 600, marginBottom: 12 }}>Rolling 20-Day Annualised Volatility (%)</div>
        <ResponsiveContainer width="100%" height={220}>
          <AreaChart data={volSeries}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0"/>
            <XAxis dataKey="date" tick={axisStyle} tickFormatter={d => d.slice(5)}/>
            <YAxis tick={axisStyle}/>
            <Tooltip contentStyle={{ fontSize: 12 }}/>
            <Area dataKey="volatility" stroke="#ef4444" fill="#fecaca" strokeWidth={2} name="Volatility %"/>
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Chart 4: Risk Probability Radar */}
      <div style={{ background: "#f8fafc", borderRadius: 12, padding: 20, border: "1px solid #e2e8f0" }}>
        <div style={{ fontWeight: 600, marginBottom: 12 }}>Risk Class Probability Distribution</div>
        <ResponsiveContainer width="100%" height={220}>
          <RadarChart data={[
            { label: "Very Low", value: 0 },
            { label: "Low", value: 0 },
            { label: "Medium", value: 0 },
            { label: "High", value: 0 },
            { label: "Very High", value: 0 },
          ]}>
            <PolarGrid/>
            <PolarAngleAxis dataKey="label" tick={{ fontSize: 11 }}/>
            <Radar dataKey="value" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.5}/>
          </RadarChart>
        </ResponsiveContainer>
        <p style={{ fontSize: 12, color: "#94a3b8", textAlign: "center", margin: 0 }}>
          Probabilities passed via props — wire from result.prediction.probabilities
        </p>
      </div>
    </div>
  );
}