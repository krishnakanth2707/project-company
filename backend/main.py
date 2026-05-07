from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yfinance as yf

from data_fetcher import fetch_price_data, fetch_news, get_company_name
from feature_engineering import compute_features
from predictor import predict_risk
from llm_analyzer import analyze_with_llm

app = FastAPI(title="Stock Risk Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    ticker: str
    period: str = "1Y"

@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    ticker = req.ticker.upper().strip()
    period = req.period

    try:
        df = fetch_price_data(ticker, period)
    except ValueError as e:
        raise HTTPException(404, str(e))

    company = get_company_name(ticker)
    news    = fetch_news(ticker, company)
    headlines = [a["title"] for a in news if a.get("title")]
    features  = compute_features(df, news)
    prediction = predict_risk(features)
    llm_output = analyze_with_llm(ticker, period, features, prediction, headlines)

    # Build chart data
    close = df["Close"].squeeze()
    volume = df["Volume"].squeeze()
    dates  = [d.strftime("%Y-%m-%d") for d in df.index]
    ma20   = close.rolling(min(20, len(close))).mean().fillna(method="bfill")
    ma50   = close.rolling(min(50, len(close))).mean().fillna(method="bfill")

    return {
        "ticker": ticker,
        "company": company,
        "period": period,
        "prediction": prediction,
        "features": features,
        "llm": llm_output,
        "headlines": headlines[:5],
        "chart_data": {
            "dates": dates,
            "prices": [round(float(p), 2) for p in close],
            "volume": [int(v) for v in volume],
            "ma20":   [round(float(v), 2) for v in ma20],
            "ma50":   [round(float(v), 2) for v in ma50],
        }
    }

@app.get("/health")
def health():
    return {"status": "ok"}