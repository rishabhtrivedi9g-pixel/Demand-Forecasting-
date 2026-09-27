# Real-Time Demand Forecasting & Inventory Optimization

End-to-end demand forecasting and inventory optimization pipeline built on the M5 Walmart Forecasting dataset.

## Project Structure

```
demand-forecasting/
├── data/
│   ├── raw/                  # Raw dataset files (calendar.csv, sales_train_validation.csv, sell_prices.csv)
│   └── processed/            # Cleaned and feature-engineered datasets
├── notebooks/                # Exploratory Data Analysis & experimentation notebooks
├── src/
│   ├── data/                 # Data loading, validation, and ingestion scripts
│   ├── features/             # Feature engineering pipelines (lags, rolling stats, calendar events)
│   ├── models/               # Model training, evaluation, and inference modules
│   └── api/                  # FastAPI inference endpoints for demand forecasting & inventory optimization
├── tests/                    # Unit and integration tests
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
└── .gitignore                # Git ignore rules
```

## Dataset Setup

The raw dataset consists of three M5 Walmart dataset files hosted on Zenodo:
1. `calendar.csv` - Date mapping, event days, SNAP flags.
2. `sales_train_validation.csv` - Historical daily sales units per item and store (d_1 to d_1913).
3. `sell_prices.csv` - Weekly selling prices per item and store.

To download and verify the raw datasets:
```bash
python src/data/download_data.py
```
