import joblib
from pathlib import Path

from src.inventory.optimizer import recommend_inventory


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = PROJECT_ROOT / "models"


# Load saved V1 inventory statistics
inventory_stats = joblib.load(
    MODEL_DIR / "inventory_stats_v1.pkl"
)

print("Inventory statistics loaded successfully.")
print("Number of item-store pairs:", len(inventory_stats))

# Take one real item-store pair
row = inventory_stats.iloc[0]

forecast_next_7_days = 10.0

result = recommend_inventory(
    forecast_next_7_days=forecast_next_7_days,
    demand_std=row["demand_std"]
)

print("\nTest pair:")
print("Item:", row["item_id"])
print("Store:", row["store_id"])

print("\nInventory recommendation:")
print(result)
