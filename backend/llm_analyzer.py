"""
Uses HuggingFace Inference API (free tier) — no GPU needed.
Model: mistralai/Mistral-7B-Instruct-v0.2 or HuggingFaceH4/zephyr-7b-beta
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

HF_API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"

def build_prompt(ticker: str, period: str, features: dict,
                 prediction: dict, news_headlines: list[str]) -> str:
    top_headlines = "\n".join(f"- {h}" for h in news_headlines[:5]) or "No recent news available."
    proba_str = ", ".join(
        f"{k}: {v*100:.1f}%" for k, v in prediction["probabilities"].items()
    )
    return f"""<|system|>
You are a professional stock risk analyst. Be concise, factual, and structured.
</s>
<|user|>
Analyse investment risk for {ticker} over {period}.

QUANTITATIVE DATA:
- ML Risk Prediction: {prediction['risk_label']} (confidence {prediction['confidence']*100:.1f}%)
- Class probabilities: {proba_str}
- ROI: {features['roi']:.2f}%
- Annualised Volatility: {features['volatility']:.2f}%
- RSI: {features['rsi']:.1f}
- Sharpe Ratio: {features['sharpe']:.2f}
- Max Drawdown: {features['max_drawdown']:.2f}%
- Price vs MA50: {features['price_vs_ma50']:.2f}%
- News Sentiment Score: {features['news_sentiment']:.3f}

RECENT NEWS HEADLINES:
{top_headlines}

Provide a structured response with exactly these three sections:

**CURRENT MARKET SUMMARY**
2–3 sentences summarising current price trend, momentum, and market position.

**RISK EXPLANATION**
2–3 sentences explaining why this risk level was assigned, referencing the specific metrics above.

**INVESTMENT OUTLOOK**
2–3 sentences on what an investor should consider for this period, including any caution flags or positive signals.
</s>
<|assistant|>"""

def analyze_with_llm(ticker: str, period: str, features: dict,
                     prediction: dict, news_headlines: list[str]) -> dict:
    prompt = build_prompt(ticker, period, features, prediction, news_headlines)
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 400,
            "temperature": 0.4,
            "top_p": 0.9,
            "do_sample": True,
            "return_full_text": False,
        }
    }
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    try:
        resp = requests.post(HF_API_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        text = data[0]["generated_text"] if isinstance(data, list) else ""
        return parse_llm_output(text)
    except Exception as e:
        return {
            "market_summary": f"LLM unavailable: {str(e)}",
            "risk_explanation": "Based on quantitative metrics only.",
            "investment_outlook": "Please review the chart data above.",
            "raw": ""
        }

def parse_llm_output(text: str) -> dict:
    sections = {
        "market_summary": "",
        "risk_explanation": "",
        "investment_outlook": "",
        "raw": text
    }
    current = None
    for line in text.split("\n"):
        l = line.strip()
        if "CURRENT MARKET SUMMARY" in l.upper():
            current = "market_summary"
        elif "RISK EXPLANATION" in l.upper():
            current = "risk_explanation"
        elif "INVESTMENT OUTLOOK" in l.upper():
            current = "investment_outlook"
        elif current and l and not l.startswith("**"):
            sections[current] += (" " + l).strip()
    return sections