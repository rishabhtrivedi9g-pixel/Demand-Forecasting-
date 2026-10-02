from src.forecasting.forecast import forecast_next_7_days
result=forecast_next_7_days(
    "HOBBIES_1_001",
    "CA_1",
    "2016-04-01"
)

print("\n7-Day Forecast")
print("----------------")

print("Item:", result["item_id"])
print("Store:", result["store_id"])
print("Start date:", result["start_date"])

print(
    "Forecast next 7 days:",
    result["forecast_next_7_days"]
)

print("\nDaily predictions:")

for day in result["daily_predictions"]:
    print(
        day["date"],
        "->",
        day["prediction"]
    )