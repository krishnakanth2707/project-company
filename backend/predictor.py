import joblib
import numpy as np
from feature_engineering import FEATURES  # reuse list

MODEL_PATH = "models/risk_model.pkl"
_artifact = None

def load_model():
    global _artifact
    if _artifact is None:
        _artifact = joblib.load(MODEL_PATH)
    return _artifact

def predict_risk(features: dict) -> dict:
    art = load_model()
    le  = art["label_encoder"]
    cal = art["calibrated"]
    feat_list = art["features"]

    X = np.array([[features[f] for f in feat_list]])
    pred_idx   = cal.predict(X)[0]
    proba      = cal.predict_proba(X)[0]
    pred_label = le.inverse_transform([pred_idx])[0]
    classes    = le.classes_

    return {
        "risk_label": pred_label,
        "probabilities": {c: round(float(p), 4) for c, p in zip(classes, proba)},
        "confidence": round(float(proba.max()), 4),
    }