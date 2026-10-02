import duckdb

con = duckdb.connect()

query = """
SELECT
    item_id,
    store_id,
    state_id,
    date,
    sales,

    -- Lag features
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

    -- Rolling features
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
    AVG(sales) OVER (
        PARTITION BY item_id, store_id
        ORDER BY date
        ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
    )
    -
    AVG(sales) OVER (
        PARTITION BY item_id, store_id
        ORDER BY date
        ROWS BETWEEN 28 PRECEDING AND 1 PRECEDING
    ) AS trend,
    STDDEV_SAMP(sales) OVER (
        PARTITION BY item_id, store_id
        ORDER BY date
        ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
    ) AS rolling_std_7,

    -- Calendar features
    dayofweek,
    month,

    EXTRACT(WEEK FROM date) AS weekofyear,

    CASE
        WHEN dayofweek IN (0, 6) THEN 1
        ELSE 0
    END AS is_weekend,

    -- Event feature
    CASE
        WHEN event_name_1 IS NOT NULL
          OR event_name_2 IS NOT NULL
        THEN 1
        ELSE 0
    END AS has_event

FROM '../data/processed/sales_processed.parquet'

WHERE item_id = 'HOBBIES_1_001'
  AND store_id = 'CA_1'

ORDER BY date
LIMIT 40
"""

df = con.execute(query).fetchdf()

print(df.to_string(index=False))