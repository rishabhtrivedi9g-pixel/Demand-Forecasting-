import joblib

from src.inventory.recommendation import (
    generate_inventory_recommendation
)


inventory_stats = joblib.load(
    "models/inventory_stats_v1.pkl"
)

item_id = "HOBBIES_1_001"
store_id = "CA_1"

stats = inventory_stats[
    (inventory_stats["item_id"] == item_id)
    & (inventory_stats["store_id"] == store_id)
].iloc[0]

result = generate_inventory_recommendation(
    item_id,
    store_id,
    "2016-04-01",
    stats["demand_std"]
)

print("\nInventory Recommendation")
print("------------------------")

for key, value in result.items():
    print(f"{key}: {value}")