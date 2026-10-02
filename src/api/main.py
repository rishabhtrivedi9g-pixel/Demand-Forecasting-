
import joblib
from datetime import date

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.inventory.recommendation import (
    generate_inventory_recommendation
)

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Demand Forecasting API",
    version="1.0.0"
)


inventory_stats = joblib.load(
    "models/inventory_stats_v1.pkl"
)



class ForecastRequest(BaseModel):
    item_id: str = Field(min_length=1)
    store_id: str = Field(min_length=1)
    start_date: date


class ForecastResponse(BaseModel):
    item_id: str
    store_id: str
    start_date: date
    forecast_next_7_days: float
    safety_stock: float
    reorder_point: float


@app.get("/")
def root():
    return {
        "message": "Demand Forecasting API is running"
    }


@app.post(
    "/forecast",
    response_model=ForecastResponse
)

def forecast(request: ForecastRequest):
    stats = inventory_stats[
        (inventory_stats["item_id"] == request.item_id)
        & (inventory_stats["store_id"] == request.store_id)
    ]

    if stats.empty:
        raise HTTPException(
            status_code=404,
            detail="Item-store pair not found"
        )

    demand_std = float(stats.iloc[0]["demand_std"])

    try:
        result = generate_inventory_recommendation(
            request.item_id,
            request.store_id,
            str(request.start_date),
            demand_std
        )
        return result

    except ValueError as error:
        logger.warning(
            "Invalid forecast request: %s",
            error
        )
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception:
        logger.exception(
            "Unexpected error while generating forecast"
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error while generating forecast"
        )