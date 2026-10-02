from numpy import quantile
import joblib
import numpy as np
from pathlib import Path
PROJECT_ROOT=Path(__file__).resolve().parents[2]
MODEL_DIR=PROJECT_ROOT/'models'

# Load trained V1 models
demand_classifier = joblib.load(
    MODEL_DIR / "demand_classifier_v1.pkl"
)

quantity_model = joblib.load(
    MODEL_DIR / "quantity_model_v1.pkl"
)

FEATURES = joblib.load(
    MODEL_DIR / "features_v1.pkl"
)

def predict_demand(features):
    """
    Generate a demand prediction for one observation.
    """
    X=features[FEATURES]
    demand_probability=demand_classifier.predict_proba(X)[:,1]
    demand_prediction=(demand_probability>=0.30).astype(int)
    quantity_log=quantity_model.predict(X)
    quantity_prediction = np.expm1(quantity_log)
    quantity_prediction = np.clip(
        quantity_prediction,
        0,
        None
    )
    # Final V1 prediction
    final_prediction = (
        quantity_prediction * demand_prediction
    )

    return {
        "demand_probability": demand_probability,
        "demand_prediction": demand_prediction,
        "quantity_prediction": quantity_prediction,
        "final_prediction": final_prediction
    }