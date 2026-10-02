import numpy as np
LEAD_TIME_DAYS_V1=7
Z_SCORE_V1=1.645
def calculate_safety_stock(demand_std,lead_time_days=LEAD_TIME_DAYS_V1,z_score=Z_SCORE_V1):
    """
    Calculate safety stock for a given demand standard deviation.
    """

    return (
        z_score
        * demand_std
        * np.sqrt(lead_time_days)
    )
def calculate_reorder_point(
    forcast_next_7_days,
    safety_stock
):
    """
    Calculate reorder point using the reorder point formula.
    """
    return forcast_next_7_days+ safety_stock
def recommend_inventory(
    forecast_next_7_days,
    demand_std
):
    """
    Generate V1 inventory recommendation.
    """

    safety_stock = calculate_safety_stock(
        demand_std
    )

    reorder_point = calculate_reorder_point(
        forecast_next_7_days,
        safety_stock
    )

    return {
        "forecast_next_7_days": forecast_next_7_days,
        "safety_stock": safety_stock,
        "reorder_point": reorder_point
    }