"""
Training strategy:
 - Synthetic but realistic data generated from real stock distributions.
 - Labels assigned by a deterministic rule engine matching domain knowledge.
 - RandomForest with class_weight='balanced' to handle class imbalance.
 - SMOTE oversampling for minority classes (Very Low / Very High).
 - StratifiedKFold CV to verify 80–90% accuracy before saving.
 - Calibrated probabilities with CalibratedClassifierCV.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import joblib, os

RISK_LABELS = ["Very Low", "Low", "Medium", "High", "Very High"]
FEATURES = [
    "roi", "volatility", "price_vs_ma20", "price_vs_ma50",
    "price_vs_ma200", "rsi", "sharpe", "max_drawdown", "news_sentiment"
]

def assign_risk_label(row: dict) -> str:
    """Rule-based labelling grounded in financial theory."""
    vol   = row["volatility"]
    roi   = row["roi"]
    dd    = row["max_drawdown"]
    rsi   = row["rsi"]
    sent  = row["news_sentiment"]
    sharpe = row["sharpe"]

    score = 0  # higher = riskier

    # Volatility (annualised %)
    if vol < 10:   score += 0
    elif vol < 20: score += 1
    elif vol < 35: score += 2
    elif vol < 50: score += 3
    else:          score += 4

    # Drawdown
    if dd > -5:    score += 0
    elif dd > -15: score += 1
    elif dd > -30: score += 2
    elif dd > -50: score += 3
    else:          score += 4

    # Sharpe ratio
    if sharpe > 1.5:  score -= 1
    elif sharpe > 0.5: score += 0
    elif sharpe > 0:   score += 1
    else:              score += 2

    # Negative ROI penalty
    if roi < -20: score += 2
    elif roi < 0: score += 1

    # RSI extremes
    if rsi > 75 or rsi < 25: score += 1

    # Negative news
    if sent < -0.2: score += 1
    elif sent > 0.2: score -= 1

    score = max(0, min(score, 8))
    # Map score → 5 classes
    if score <= 1:   return "Very Low"
    elif score <= 3: return "Low"
    elif score <= 5: return "Medium"
    elif score <= 6: return "High"
    else:            return "Very High"

def generate_training_data(n: int = 8000) -> pd.DataFrame:
    np.random.seed(42)
    records = []
    for _ in range(n):
        vol  = np.random.lognormal(mean=2.8, sigma=0.6)   # realistic: 5–80%
        roi  = np.random.normal(loc=vol * 0.3, scale=vol * 0.8)
        dd   = -abs(np.random.normal(loc=vol * 0.5, scale=vol * 0.3))
        rsi  = np.clip(np.random.normal(50, 18), 5, 95)
        sharpe = np.random.normal(0.6, 0.8)
        sent = np.random.normal(0, 0.25)
        # MA offsets correlated with trend
        trend = roi / 20  # positive ROI → price above MA
        r = {
            "volatility": vol,
            "roi": roi,
            "max_drawdown": dd,
            "rsi": rsi,
            "sharpe": sharpe,
            "news_sentiment": np.clip(sent, -1, 1),
            "price_vs_ma20":  np.random.normal(trend * 2, 3),
            "price_vs_ma50":  np.random.normal(trend * 3, 5),
            "price_vs_ma200": np.random.normal(trend * 5, 8),
        }
        r["label"] = assign_risk_label(r)
        records.append(r)
    return pd.DataFrame(records)

def train_and_save(model_path: str = "models/risk_model.pkl"):
    os.makedirs("models", exist_ok=True)
    df = generate_training_data(8000)

    # Check label distribution
    print("Label distribution:")
    print(df["label"].value_counts())

    X = df[FEATURES].values
    y = df["label"].values

    le = LabelEncoder()
    le.fit(RISK_LABELS)
    y_enc = le.transform(y)

    # SMOTE to balance minority classes, then RandomForest
    rf = RandomForestClassifier(
        n_estimators=300,
        max_depth=12,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    pipeline = ImbPipeline([
        ("smote", SMOTE(random_state=42, k_neighbors=5)),
        ("clf", rf),
    ])

    # Stratified cross-validation BEFORE saving
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(pipeline, X, y_enc, cv=skf, scoring="accuracy")
    print(f"\nCV Accuracy: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
    if cv_scores.mean() < 0.78:
        raise RuntimeError(f"Accuracy too low ({cv_scores.mean():.2f}). Check features/labels.")

    # Fit on all data
    pipeline.fit(X, y_enc)

    # Calibrated probabilities on full model (wrap RF only)
    rf_fitted = pipeline.named_steps["clf"]
    calibrated = CalibratedClassifierCV(rf_fitted, method="isotonic", cv="prefit")
    X_smoted, y_smoted = SMOTE(random_state=42).fit_resample(X, y_enc)
    calibrated.fit(X_smoted, y_smoted)

    artifact = {
        "pipeline": pipeline,
        "calibrated": calibrated,
        "label_encoder": le,
        "features": FEATURES,
        "cv_mean": float(cv_scores.mean()),
    }
    joblib.dump(artifact, model_path)
    print(f"\nModel saved to {model_path}")
    print(f"Final CV accuracy: {cv_scores.mean()*100:.1f}%")

if __name__ == "__main__":
    train_and_save()