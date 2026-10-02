import duckdb
import pandas as pd
from pathlib import Path
from src.features.encoders import encode_features


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PARQUET_PATH = PROJECT_ROOT / "data" / "processed" / "sales_processed.parquet"


def generate_features(item_id, store_id, target_date):
    """
    Generate V1 features for one item-store-date observation.
    """

    con = duckdb.connect()

    query = f"""
    WITH base AS (
        SELECT
            item_id,
            store_id,
            state_id,
            date,
            sales,
            dayofweek,
            month,
            event_name_1,
            event_name_2,

            LAG(sales, 1) OVER (
                PARTITION BY item_id, store_id
                ORDER BY date
            ) AS lag_1,

            LAG(sales, 7) OVER (
                PARTITION BY item_id, store_id
                ORDER BY date
            ) AS lag_7,

            LAG(sales, 14) OVER (
                PARTITION BY item_id, store_id
                ORDER BY date
            ) AS lag_14,

            LAG(sales, 28) OVER (
                PARTITION BY item_id, store_id
                ORDER BY date
            ) AS lag_28,

            AVG(sales) OVER (
                PARTITION BY item_id, store_id
                ORDER BY date
                ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
            ) AS rolling_mean_7,

            AVG(sales) OVER (
                PARTITION BY item_id, store_id
                ORDER BY date
                ROWS BETWEEN 28 PRECEDING AND 1 PRECEDING
            ) AS rolling_mean_28,

            MAX(sales) OVER (
                PARTITION BY item_id, store_id
                ORDER BY date
                ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
            ) AS rolling_max_7,

            MAX(sales) OVER (
                PARTITION BY item_id, store_id
                ORDER BY date
                ROWS BETWEEN 28 PRECEDING AND 1 PRECEDING
            ) AS rolling_max_28,

            STDDEV_SAMP(sales) OVER (
                PARTITION BY item_id, store_id
                ORDER BY date
                ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
            ) AS rolling_std_7

        FROM read_parquet('{PARQUET_PATH}')
        WHERE item_id = ?
          AND store_id = ?
    ),

    features AS (
        SELECT
            *,
            rolling_mean_7 - rolling_mean_28 AS trend,

            EXTRACT(WEEK FROM date) AS weekofyear,

            CASE
                WHEN dayofweek IN (0, 6) THEN 1
                ELSE 0
            END AS is_weekend,

            CASE
                WHEN event_name_1 IS NOT NULL
                  OR event_name_2 IS NOT NULL
                THEN 1
                ELSE 0
            END AS has_event

        FROM base
    )

    SELECT *
    FROM features
    WHERE date = ?
    """

    df = con.execute(
        query,
        [item_id, store_id, target_date]
    ).df()

    con.close()

    if df.empty:
        raise ValueError(
            f"No data found for {item_id}, {store_id}, {target_date}"
        )
    df = encode_features(df)

    return df