# Real-Time Demand Forecasting & Inventory Optimization Platform

> **Current Status: V1.0 — Core ML and Inventory Optimization Pipeline Completed**
>
> This project is currently under active development. Version 1 focuses on building and evaluating the core demand forecasting and inventory recommendation pipeline. Production API integration, automated pipelines, monitoring, deployment, and additional forecasting improvements are planned for future versions.

---

## Overview

The **Real-Time Demand Forecasting & Inventory Optimization Platform** is an end-to-end machine learning project designed to predict short-term product demand and translate those predictions into inventory decisions.

The system combines:

- Historical sales data
- Temporal demand patterns
- Rolling demand statistics
- Calendar information
- Product, store, and state information
- A two-stage machine learning architecture
- Short-term demand forecasting
- Safety-stock calculation
- Reorder-point optimization

The ultimate goal is to move beyond simply predicting:

> **"How much will be sold?"**

and instead answer:

> **"How much inventory should be maintained to reduce stockouts while controlling excess inventory?"**

The current implementation uses the **M5 Forecasting dataset** and simulates a real-time forecasting environment using historical daily sales data.

---

# Project Status

## V1.0

**V1 is the first complete experimental version of the system.**

The current version includes:

- [x] M5 sales data processing
- [x] Wide-to-long sales transformation
- [x] Temporal feature engineering
- [x] Lag features
- [x] Rolling demand features
- [x] Calendar features
- [x] Product/store/state encoding
- [x] XGBoost demand classifier
- [x] XGBoost quantity regression model
- [x] Two-stage demand forecasting
- [x] Demand threshold optimization
- [x] 7-day demand forecasting
- [x] Safety-stock calculation
- [x] Reorder-point calculation
- [x] Inventory service-level evaluation
- [x] Model serialization
- [x] Basic inference pipeline
- [x] Inventory optimizer module
- [x] Unit testing for inventory calculations

### Still under development

- [ ] Production-ready real-time API
- [ ] FastAPI integration
- [ ] Automated feature generation during inference
- [ ] Database integration
- [ ] Redis caching
- [ ] Model monitoring
- [ ] MLflow experiment tracking
- [ ] Automated retraining
- [ ] Cloud deployment
- [ ] Production inventory simulator
- [ ] Dashboard
- [ ] Advanced forecasting models
- [ ] Forecast uncertainty / prediction intervals

---

# System Architecture

```text
                    Historical Sales Data
                            │
                            ▼
                  Data Processing Pipeline
                            │
                            ▼
                  Feature Engineering
                            │
          ┌─────────────────┴─────────────────┐
          │                                   │
          ▼                                   ▼
   Demand Classifier                   Quantity Regressor
   "Will demand occur?"                "How much demand?"
          │                                   │
          └─────────────────┬─────────────────┘
                            │
                            ▼
                  Final Demand Prediction
                            │
                            ▼
                 7-Day Demand Forecast
                            │
                            ▼
                    Safety Stock
                            │
                            ▼
                    Reorder Point
                            │
                            ▼
                Inventory Recommendation
Dataset

The project uses the M5 Forecasting dataset, which contains hierarchical Walmart sales data.

The dataset includes information about:

Products
Departments
Categories
Stores
States
Daily sales
Calendar events
Product prices

The original sales data is provided in a wide format and is transformed into a long-format representation for feature engineering.

Processed dataset

The sales data contains approximately:

58,327,370 observations

The processed dataset includes fields such as:

id
item_id
dept_id
cat_id
store_id
state_id
d
sales
date
wm_yr_wk
weekday
wday
month
year
event_name_1
event_type_1
event_name_2
event_type_2
snap_CA
snap_TX
snap_WI
sell_price
week
day
dayofweek
Feature Engineering

V1 uses the following 18 model features:

lag_1
lag_7
lag_14
lag_28

rolling_mean_7
rolling_mean_28
rolling_max_7
rolling_max_28
rolling_std_7

trend

dayofweek
month
weekofyear
is_weekend
has_event

state_encoded
store_encoded
item_encoded
Lag Features

Historical demand is used to capture short-term and weekly demand patterns.

Examples:

lag_1
lag_7
lag_14
lag_28

These represent demand from:

Previous day
Previous week
Two weeks earlier
Four weeks earlier
Rolling Features

Rolling statistics capture local demand behavior:

rolling_mean_7
rolling_mean_28
rolling_max_7
rolling_max_28
rolling_std_7

These provide information about:

Recent average demand
Longer-term average demand
Recent demand spikes
Demand variability
Calendar Features

The model also uses:

dayofweek
month
weekofyear
is_weekend
has_event

These allow the model to learn weekly and seasonal patterns.

V1 Machine Learning Architecture

V1 uses a two-stage XGBoost architecture.

Stage 1: Demand Classification

The first model predicts whether demand will occur.

P(demand > 0)

Instead of directly predicting the quantity, the classifier determines whether the observation is likely to have positive demand.

Stage 2: Quantity Regression

For observations with positive historical demand, a second XGBoost regression model predicts demand quantity.

The target is transformed using:

log1p(sales)

The prediction is converted back using:

expm1(prediction)

This helps handle the highly skewed distribution of retail sales.

V1 Prediction Pipeline

The final prediction is generated as:

Demand Probability
        │
        ▼
Threshold = 0.30
        │
        ├── 0 → Demand = 0
        │
        └── 1 → Use quantity prediction
                         │
                         ▼
                  Final Prediction

The operational threshold selected for V1 is:

0.30

This threshold was selected based on the inventory objective rather than forecasting accuracy alone.

A lower threshold increases the number of predicted demand-positive days, which affects stockout and excess-inventory behavior.

Model Experiments

The project was developed through multiple model iterations rather than directly jumping to the final model.

The following results are from the experimental development process.

Version Comparison
Version	Main Change	MAE	RMSE
Baseline	Naive forecast	1.2083	1.6708
RF V1	Random Forest + engineered features	0.8969	1.1127
RF V2	Added calendar features	0.9017	1.1309
RF V3	Added price information	0.8966	1.1234
RF V4	Added lag-28	0.8823	1.0852
Multi-Series RF V4	Multiple item-store pairs	1.0655	1.6160
XGBoost V4	XGBoost replacement	1.0325	1.5906
V5	Added trend feature	1.0206	—
V6	Calendar/event improvements	0.9876	—
V8	Added rolling maximum	0.9763	—
V10	Expanded multi-series model	0.6784	1.2718
V11	Two-stage classifier + regression	0.6486	1.1736
V12	Log-transformed quantity regression	0.6254	1.1461

Metrics are reported from the corresponding experimental evaluation runs. Different experiments used different subsets/time windows, so the numbers should not be interpreted as a perfectly controlled benchmark across every version.

V12 Results

The V12 architecture produced the following April evaluation results:

MAE  : 0.62538
RMSE : 1.14605

For comparison, the naive baseline achieved:

MAE  : 1.25278

This corresponds to approximately:

50.1% reduction in MAE

relative to the naive April baseline used in the experiment.

For March:

V12 MAE  : 0.66141
Naive MAE: 1.23333

This corresponds to approximately:

46.4% reduction in MAE
Classification Performance

The V1 classifier was also evaluated independently.

At the original threshold of 0.50:

Accuracy  : 71.92%
Precision : 72.59%
Recall    : 42.70%
F1 Score  : 53.77%

The threshold experiment showed that a threshold of 0.30 produced:

Precision : 54.0%
Recall    : 73.9%
F1 Score  : 62.4%

However, the lower classification threshold did not produce the best raw forecasting MAE.

This is an important design decision in V1:

The forecasting threshold is treated as an operational inventory parameter rather than being selected solely from classification metrics.

Forecasting vs Inventory Optimization

A key objective of this project is to demonstrate that the best forecasting metric does not necessarily correspond to the best inventory behavior.

Two classifier thresholds were evaluated.

Metric	Threshold 0.50	Threshold 0.30
Service Level	69.41%	87.41%
Stockout Rate	30.59%	12.59%
Average Shortage	0.504	0.159
Average Excess Inventory	3.085	5.739
Forecast MAE	0.625	0.771
Forecast RMSE	1.146	1.186

The 0.30 threshold substantially reduced stockouts and shortages, but increased excess inventory.

This illustrates the central trade-off of the project:

Higher forecast sensitivity
        ↓
Fewer stockouts
        ↓
More inventory
        ↓
Higher excess stock

V1 therefore uses:

Operational threshold = 0.30

for the inventory-oriented inference pipeline.

Inventory Optimization

The inventory component uses a reorder-point approach.

Lead Time

V1 assumes:

Supplier lead time = 7 days
Safety Stock

Safety stock is calculated using:

Safety Stock =
Z × Demand Standard Deviation × √Lead Time

V1 uses:

Z = 1.645
Lead Time = 7 days

which corresponds approximately to a 95% one-sided service-level assumption under the underlying statistical approximation.

Reorder Point

The reorder point is:

Reorder Point =
Forecasted 7-Day Demand + Safety Stock

The resulting recommendation can therefore be interpreted as:

Maintain approximately this amount of inventory before triggering replenishment.

V1 Inventory Evaluation

The inventory evaluation was performed across:

50 item-store pairs

with:

17 valid evaluation windows per pair

for a total of:

850 evaluation observations

Using the V1 operational threshold of 0.30:

Service Level : 87.41%
Stockout Rate : 12.59%
Avg Shortage  : 0.159
Avg Excess     : 5.739

These results represent a reorder-point stress test, not a full production inventory simulator.

The current evaluation does not model every real-world inventory event such as:

Existing on-hand inventory
Purchase orders
Shipment arrivals
Lost sales
Supplier constraints
Variable lead times
Holding costs
Ordering costs

Those are planned improvements for later versions.

Why V1 Is Not the Final System

V1 is intentionally treated as a foundation rather than a finished production system.

Current limitations include:

1. Historical dataset

The M5 dataset is historical.

Therefore, "real-time" in this project currently refers to the intended architecture of daily reforecasting, rather than a genuine live retail data stream.

Future versions will simulate or support incoming daily observations through an API.

2. Forecasting horizon

The current inventory evaluation uses a 7-day forecasting window.

The system will eventually support configurable forecasting horizons.

3. Safety-stock estimation

V1 calculates safety stock using historical demand variability.

A future version can use:

forecast residuals

instead of raw historical demand deviation.

4. Inventory simulation

The current inventory evaluation is based on reorder-point calculations.

It is not yet a full inventory simulator.

5. Production inference pipeline

The trained models are serialized and can be loaded for inference, but automated production feature generation is still being implemented.

Project Structure
demand-forecasting/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── models/
│   ├── demand_classifier_v1.pkl
│   ├── quantity_model_v1.pkl
│   ├── features_v1.pkl
│   └── inventory_stats_v1.pkl
│
├── notebooks/
│   ├── data_understanding.ipynb
│   ├── feature_engineering copy.ipynb
│   └── model_training.ipynb
│
├── src/
│   ├── data/
│   ├── features/
│   ├── models/
│   │   └── inference.py
│   ├── inventory/
│   │   └── optimizer.py
│   └── api/
│
├── tests/
│   ├── test_inference.py
│   └── test_inventory.py
│
├── requirements.txt
├── README.md
└── .gitignore
Technology Stack
Machine Learning
Python
pandas
NumPy
scikit-learn
XGBoost
Data Processing
DuckDB
Parquet
pandas
Backend / Production

Planned:

FastAPI
PostgreSQL
Redis
Docker
MLOps

Planned:

MLflow
Automated retraining
Model monitoring
Deployment

Planned:

AWS / Railway / Render
Installation

Clone the repository:

git clone https://github.com/<your-username>/demand-forecasting.git
cd demand-forecasting

Create a virtual environment:

python -m venv .venv

Activate it on Windows:

.venv\Scripts\Activate.ps1

Install dependencies:

pip install -r requirements.txt
Running Tests

From the project root:

$env:PYTHONPATH = (Get-Location).Path

Then:

python tests/test_inventory.py

and:

python tests/test_inference.py
Model Inference

The V1 inference pipeline loads:

demand_classifier_v1.pkl
quantity_model_v1.pkl
features_v1.pkl

The inference process produces:

Demand probability
        ↓
Demand classification
        ↓
Quantity prediction
        ↓
Final demand prediction

Example output:

Demand probability : 0.613
Demand prediction  : 1
Quantity prediction: 1.665
Final prediction   : 1.665
Roadmap
V1.0 — Core ML + Inventory

Current version

Focus:

Feature engineering
Demand forecasting
Two-stage XGBoost model
Inventory calculations
Reorder point
Initial evaluation
V1.1 — Production Inference

Planned:

Real feature generation from incoming data
Automated 7-day forecast generation
Complete inference pipeline
Better input validation
Improved tests
V2.0 — API + Real-Time Simulation

Planned:

Incoming daily sales
        ↓
Feature generation
        ↓
Model inference
        ↓
Demand forecast
        ↓
Inventory recommendation

Technology:

FastAPI
PostgreSQL
Redis
Docker
V3.0 — MLOps

Planned:

MLflow
Experiment tracking
Model registry
Automated retraining
Model monitoring
Data drift detection
V4.0 — Advanced Forecasting

Potential improvements:

LightGBM
Temporal Fusion Transformer
Deep learning models
Probabilistic forecasting
Prediction intervals
Quantile regression
Forecast ensembles
Future Dashboard

The eventual system is intended to expose information such as:

Product: HOBBIES_1_001
Store: CA_1

Forecasted demand (7 days): 127 units
Safety stock:               16 units
Reorder point:              143 units

Stockout risk:              8%
Recommended inventory:      143 units

The dashboard will allow users to inspect demand forecasts, inventory recommendations, historical demand, and model performance.

Important Note

This project is currently V1.0 and is not a finished production system.

The reported model performance is based on controlled experiments using the M5 historical dataset. It should not be interpreted as proof of performance on a live retail environment.

The main purpose of V1 is to establish the complete technical foundation:

Data
 ↓
Feature Engineering
 ↓
Machine Learning
 ↓
Forecasting
 ↓
Inventory Optimization
 ↓
Evaluation

Future versions will focus on productionization, real-time inference, monitoring, deployment, and more advanced forecasting techniques.

Author

Rishabh Trivedi

B.Tech Computer Science / Data Science

Interested in:

Machine Learning
Data Science
Backend Engineering
MLOps
Applied AI
Project Status

Current Version: V1.0

🚧 Active Development
