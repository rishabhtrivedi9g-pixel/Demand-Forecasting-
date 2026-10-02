import pandas as pd

from src.models.inference import predict_demand, FEATURES


# One test observation
test_data = {
    "lag_1": 1,
    "lag_7": 2,
    "lag_14": 1,
    "lag_28": 2,
    "rolling_mean_7": 1.5,
    "rolling_mean_28": 1.7,
    "rolling_max_7": 4,
    "rolling_max_28": 6,
    "rolling_std_7": 1.0,
    "trend": 0.1,
    "dayofweek": 2,
    "month": 4,
    "weekofyear": 14,
    "is_weekend": 0,
    "has_event": 0,
    "state_encoded": 0,
    "store_encoded": 0,
    "item_encoded": 0
}

features = pd.DataFrame([test_data])

result = predict_demand(features)

print("Inference successful!")
print("Demand probability:", result["demand_probability"])
print("Demand prediction:", result["demand_prediction"])
print("Quantity prediction:", result["quantity_prediction"])
print("Final prediction:", result["final_prediction"])