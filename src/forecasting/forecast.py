from datetime import datetime, timedelta

from src.features.generator import generate_features
from src.models.inference import predict_demand


def forecast_next_7_days(item_id, store_id, start_date):
    """
    Generate a 7-day demand forecast using daily historical feature generation.
    """

    start_date = datetime.strptime(
        start_date, "%Y-%m-%d"
    ).date()

    daily_predictions = []

    for i in range(7):
        current_date = start_date + timedelta(days=i)

        features = generate_features(
            item_id,
            store_id,
            str(current_date)
        )

        result = predict_demand(features)

        prediction = float(
            result["final_prediction"][0]
        )

        daily_predictions.append({
            "date": str(current_date),
            "prediction": prediction
        })

    total_forecast = sum(
        day["prediction"]
        for day in daily_predictions
    )

    return {
        "item_id": item_id,
        "store_id": store_id,
        "start_date": str(start_date),
        "forecast_next_7_days": total_forecast,
        "daily_predictions": daily_predictions
    }
