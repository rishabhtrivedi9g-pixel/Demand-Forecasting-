from src.features.generator import generate_features
from src.models.inference import predict_demand


features = generate_features(
    "HOBBIES_1_001",
    "CA_1",
    "2016-04-01"
)

result = predict_demand(features)

print("\nInference result:")
print("Demand probability:", result["demand_probability"])
print("Demand prediction:", result["demand_prediction"])
print("Quantity prediction:", result["quantity_prediction"])
print("Final prediction:", result["final_prediction"])