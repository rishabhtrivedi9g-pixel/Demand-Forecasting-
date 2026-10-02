# Real-Time Demand Forecasting & Inventory Optimization Platform

**Version:** V1.0\
**Status:** Core ML pipeline, 7-day forecast workflow, inventory
recommendations, and FastAPI endpoint implemented. Productionization
remains ongoing.

An end-to-end machine learning project that predicts short-term retail
demand and translates those predictions into inventory recommendations.
The project uses the M5 Forecasting dataset to develop and evaluate a
daily forecasting workflow.

> **About "real-time":** The current system uses historical M5 data.
> "Real-time" describes the intended daily reforecasting workflow, not a
> live retail data stream.

## Overview

The platform combines:

-   Historical sales and calendar data
-   Lag, rolling, trend, and calendar features
-   A two-stage XGBoost architecture
-   Seven-day demand forecasting
-   Safety-stock and reorder-point calculations
-   A FastAPI inference endpoint
-   Tests for core pipeline and API behavior

The objective is not only to estimate how much may sell, but also to
translate demand estimates into inventory decisions while making the
trade-off between stockouts and excess inventory visible.

## Current implementation

### Implemented in V1.0

-   M5 sales data processing and wide-to-long transformation
-   Parquet-based data handling with DuckDB
-   Temporal feature engineering
-   Product, store, and state encoding
-   XGBoost demand classifier
-   XGBoost quantity regressor trained on `log1p(sales)`
-   Two-stage demand prediction
-   Seven-day forecast generation
-   Safety-stock and reorder-point calculations
-   Inventory stress-test evaluation
-   Serialized model artifacts
-   Feature generation during inference
-   FastAPI `/forecast` endpoint with request validation and error
    handling
-   Tests for API, features, forecasting, recommendations, and pipeline
    behavior

### Not yet implemented as production capabilities

-   Live retail data ingestion
-   Production database integration
-   Redis caching
-   Model monitoring and data-drift detection
-   Automated retraining and model registry
-   Cloud deployment
-   A full event-driven inventory simulator
-   Dashboard and user interface
-   Calibrated prediction intervals or probabilistic forecasts

## Architecture

``` text
Historical M5 data
       |
       v
Data processing and Parquet
       |
       v
Feature generation
       |
       v
Demand classifier ---- Quantity regressor
       |                       |
       +-----------+-----------+
                   |
                   v
          Demand prediction
                   |
                   v
          7-day forecast
                   |
                   v
       Safety stock and reorder point
                   |
                   v
       Inventory recommendation
                   |
                   v
             FastAPI endpoint
```

## Dataset

The project uses the [M5 Forecasting
dataset](https://www.kaggle.com/competitions/m5-forecasting-accuracy/data),
which contains hierarchical Walmart sales data, calendar events, and
product prices.

The transformed long-format sales data contains approximately
**58,327,370 observations**.

The original and processed datasets are excluded from this repository
because of their size. Download the competition data from Kaggle and
place the files locally in the following structure:

``` text
data/
├── raw/
│   ├── calendar.csv
│   ├── sales_train_validation.csv
│   └── sell_prices.csv
└── processed/
    └── sales_processed.parquet
```

## Feature engineering

The V1 model uses 18 features.

  -----------------------------------------------------------------------
  Group                               Features
  ----------------------------------- -----------------------------------
  Lag                                 `lag_1`, `lag_7`, `lag_14`,
                                      `lag_28`

  Rolling                             `rolling_mean_7`,
                                      `rolling_mean_28`, `rolling_max_7`,
                                      `rolling_max_28`, `rolling_std_7`

  Trend                               `trend`

  Calendar                            `dayofweek`, `month`, `weekofyear`,
                                      `is_weekend`, `has_event`

  Encoded identifiers                 `state_encoded`, `store_encoded`,
                                      `item_encoded`
  -----------------------------------------------------------------------

These features represent recent demand, weekly patterns, local
variability, calendar effects, and product/store context.

## Machine learning approach

V1 uses two XGBoost models:

1.  **Demand classifier:** estimates the probability that demand is
    positive.
2.  **Quantity regressor:** predicts demand quantity for positive-demand
    observations. The target is transformed using `log1p(sales)` and
    converted back using `expm1` during prediction.

The current V1 inference configuration uses a classifier threshold of
**0.50**. Threshold 0.30 was also evaluated as an inventory-oriented
alternative. The choice affects the balance between missed demand and
excess inventory.

## Model experiments and results

The project was developed through multiple experiments. The results
below come from their respective evaluation runs.

  Experiment           Main change                                       MAE         RMSE
  -------------------- ---------------------------------------- ------------ ------------
  Baseline             Naive forecast                                 1.2083       1.6708
  RF V1                Random Forest with engineered features         0.8969       1.1127
  RF V2                Added calendar features                        0.9017       1.1309
  RF V3                Added price information                        0.8966       1.1234
  RF V4                Added lag-28                                   0.8823       1.0852
  Multi-Series RF V4   Multiple item-store pairs                      1.0655       1.6160
  XGBoost V4           XGBoost replacement                            1.0325       1.5906
  V5                   Added trend feature                            1.0206          ---
  V6                   Calendar/event improvements                    0.9876          ---
  V8                   Added rolling maximum                          0.9763          ---
  V10                  Expanded multi-series model                    0.6784       1.2718
  V11                  Two-stage classifier and regression            0.6486       1.1736
  V12                  Log-transformed quantity regression        **0.6254**   **1.1461**

V12's April evaluation reported:

-   **MAE:** 0.62538
-   **RMSE:** 1.14605
-   **Naive baseline MAE:** 1.25278
-   **MAE reduction:** approximately 50.1% against that April baseline

For March, V12 MAE was 0.66141 versus 1.23333 for the naive baseline, a
reduction of approximately 46.4%.

The experiments did not all use identical data subsets and time windows.
The table is a development history, not a perfectly controlled benchmark
across every version. MAE and RMSE are error metrics, not accuracy
percentages.

## Inventory evaluation

The inventory component uses a reorder-point approach with a seven-day
lead-time assumption.

Safety stock is calculated as:

``` text
Safety Stock = Z × Demand Standard Deviation × √Lead Time
```

The reorder point is:

``` text
Reorder Point = Forecasted 7-Day Demand + Safety Stock
```

The stress test evaluated 50 item-store pairs over 17 windows per pair,
for **850 evaluation observations**.

The recorded threshold comparison was:

  Metric                       Threshold 0.50   Threshold 0.30
  -------------------------- ---------------- ----------------
  Service level                        69.41%           87.41%
  Stockout rate                        30.59%           12.59%
  Average shortage                      0.504            0.159
  Average excess inventory              3.085            5.739
  Forecast MAE                          0.625            0.771
  Forecast RMSE                         1.146            1.186

In this evaluation, threshold 0.30 reduced stockouts and shortages while
increasing excess inventory and forecast error. The current inference
configuration is 0.50; the 0.30 result is retained as a documented
alternative from the inventory experiment.

These results come from a reorder-point stress test, not a full
production inventory simulator. The evaluation does not model every
real-world event, such as on-hand stock, open purchase orders, shipment
arrivals, lost sales, supplier constraints, variable lead times, or
holding and ordering costs.

## FastAPI

The API is implemented in `src/api/main.py`.

-   `GET /` provides a basic application route.
-   `POST /forecast` accepts `item_id`, `store_id`, and `start_date`.
-   Request validation rejects empty identifiers and malformed inputs.
-   Unknown item/store combinations return a not-found response.
-   Invalid date ranges are handled as client errors.
-   Unexpected failures are logged and returned as generic server
    errors.

### Run locally

From the project root, create and activate a virtual environment.

**Windows PowerShell:**

``` powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Start the API:

``` powershell
python -m uvicorn src.api.main:app --reload
```

Open the interactive documentation:

``` text
http://127.0.0.1:8000/docs
```

The API requires the model artifacts and processed data at the paths
expected by the project. The dataset is not bundled with the repository.

## Tests

Run the test suite from the project root:

``` powershell
python -m pytest tests/
```

The tests cover API behavior and validation, feature generation,
forecasting, inventory recommendations, and pipeline-related
functionality.

## Project structure

``` text
Demand forecasting/
├── data/
│   ├── raw/                  # Local dataset files; excluded from Git
│   └── processed/            # Local processed data; excluded from Git
├── models/
│   ├── demand_classifier_v1.pkl
│   ├── quantity_model_v1.pkl
│   ├── features_v1.pkl
│   └── inventory_stats_v1.pkl
├── notebooks/                # Data exploration and model experiments
├── src/
│   ├── api/
│   │   └── main.py
│   ├── features/
│   │   ├── encoders.py
│   │   └── generator.py
│   ├── forecasting/
│   │   └── forecast.py
│   └── inventory/
│       ├── optimizer.py
│       └── recommendation.py
├── tests/
├── requirements.txt
└── README.md
```

Other experimental model artifacts may be present in `models/`. The
files listed above are the V1 inference artifacts.

## Technology stack

-   **Language:** Python
-   **Data processing:** pandas, NumPy, DuckDB, Parquet
-   **Machine learning:** XGBoost, scikit-learn
-   **Backend:** FastAPI, Pydantic
-   **Testing:** pytest

PostgreSQL, Redis, MLflow, automated retraining, monitoring, and cloud
deployment are possible future additions rather than current production
capabilities.

## Limitations and next steps

-   The source data is historical, not a live retail feed.
-   The forecast workflow simulates daily forecasting over historical
    data; it is not yet a fully recursive future forecasting system.
-   Safety stock currently uses historical demand variability rather
    than calibrated forecast-error distributions.
-   Inventory evaluation is not a complete event-driven simulation.
-   Database-backed ingestion, caching, monitoring, retraining, and
    deployment remain future work.

Potential next steps include improving future-date inference, expanding
the inventory simulator, evaluating forecast uncertainty, adding
experiment tracking and monitoring, and deploying the API.

## Author

**Rishabh Trivedi**\
B.Tech, Computer Science

Interests: Machine Learning, Data Science, Backend Engineering, MLOps,
and Applied AI.

------------------------------------------------------------------------

**Project status:** V1.0, active development. Reported performance is
based on experiments using the M5 historical dataset and should not be
interpreted as proof of performance on a live retail environment.
