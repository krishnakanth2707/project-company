import pandas as pd
import numpy as np
from textblob import TextBlob
import ta

def compute_features(df: pd.DataFrame, news_articles: list) -> dict:
    close = df["Close"].squeeze()

    # ── ROI ──────────────────────────────────────────────
    roi = float((close.iloc[-1] - close.iloc[0]) / close.iloc[0] * 100)

    # ── Volatility (annualised) ───────────────────────────
    daily_returns = close.pct_change().dropna()
    volatility = float(daily_returns.std() * np.sqrt(252) * 100)

    # ── Moving Averages ───────────────────────────────────
    ma20  = float(close.rolling(min(20,  len(close))).mean().iloc[-1])
    ma50  = float(close.rolling(min(50,  len(close))).mean().iloc[-1])
    ma200 = float(close.rolling(min(200, len(close))).mean().iloc[-1])
    price = float(close.iloc[-1])

    # Price vs MA ratios (scale-free)
    price_vs_ma20  = (price - ma20)  / ma20  * 100 if ma20  else 0
    price_vs_ma50  = (price - ma50)  / ma50  * 100 if ma50  else 0
    price_vs_ma200 = (price - ma200) / ma200 * 100 if ma200 else 0

    # ── RSI ──────────────────────────────────────────────
    rsi = float(ta.momentum.RSIIndicator(close, window=14).rsi().iloc[-1])

    # ── Sharpe-like ratio ─────────────────────────────────
    mean_ret = daily_returns.mean()
    std_ret  = daily_returns.std()
    sharpe   = float(mean_ret / std_ret * np.sqrt(252)) if std_ret else 0

    # ── Max drawdown ──────────────────────────────────────
    roll_max = close.cummax()
    drawdown = (close - roll_max) / roll_max
    max_dd   = float(drawdown.min() * 100)

    # ── News sentiment ────────────────────────────────────
    sentiments = []
    for art in news_articles[:15]:
        text = f"{art.get('title','')} {art.get('description','')}"
        blob = TextBlob(text)
        sentiments.append(blob.sentiment.polarity)
    avg_sentiment = float(np.mean(sentiments)) if sentiments else 0.0
    news_count = len(news_articles)

    return {
        "roi": roi,
        "volatility": volatility,
        "price_vs_ma20": price_vs_ma20,
        "price_vs_ma50": price_vs_ma50,
        "price_vs_ma200": price_vs_ma200,
        "rsi": rsi,
        "sharpe": sharpe,
        "max_drawdown": max_dd,
        "news_sentiment": avg_sentiment,
        "news_count": news_count,
        # Raw values for display
        "current_price": price,
        "ma20": ma20, "ma50": ma50, "ma200": ma200,
    }