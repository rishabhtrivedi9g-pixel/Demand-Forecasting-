from src.features.generator import generate_features


df = generate_features(
    "HOBBIES_1_001",
    "CA_1",
    "2016-04-01"
)

print("\nGenerated feature row:")
print(df.to_string(index=False))

print("\nV1 model features:")
print(df[
    [
        "lag_1",
        "lag_7",
        "lag_14",
        "lag_28",
        "rolling_mean_7",
        "rolling_mean_28",
        "rolling_max_7",
        "rolling_max_28",
        "rolling_std_7",
        "trend",
        "dayofweek",
        "month",
        "weekofyear",
        "is_weekend",
        "has_event",
        "state_encoded",
        "store_encoded",
        "item_encoded"
    ]
].to_string(index=False))