from src.forecasting.forecast import forecast_next_7_days
from src.inventory.optimizer import recommend_inventory


def generate_inventory_recommendation(
    item_id,
    store_id,
    start_date,
    demand_std
):
    """
    Generate a 7-day demand forecast and inventory recommendation.
    """

    forecast_result = forecast_next_7_days(
        item_id,
        store_id,
        start_date
    )

    inventory_result = recommend_inventory(
        forecast_result["forecast_next_7_days"],
        demand_std
    )

    return {
        "item_id": item_id,
        "store_id": store_id,
        "start_date": start_date,
        "forecast_next_7_days": inventory_result[
            "forecast_next_7_days"
        ],
        "safety_stock": inventory_result[
            "safety_stock"
        ],
        "reorder_point": inventory_result[
            "reorder_point"
        ]
    }