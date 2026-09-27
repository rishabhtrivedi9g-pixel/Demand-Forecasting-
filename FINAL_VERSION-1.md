                ┌──────────────┐
                │  V1 ML Model │
                └──────┬───────┘
                       ↓
              ┌─────────────────┐
              │ Inference Layer │
              └────────┬────────┘
                       ↓
                 ┌───────────┐
                 │  FastAPI  │
                 └─────┬─────┘
                       ↓
              ┌─────────────────┐
              │ Docker Container│
              └───────┬─────────┘
                      ↓
              Prediction API
                      ↓
       ┌──────────────┴──────────────┐
       ↓                             ↓
 Demand Forecast              Inventory Advice
       ↓                             ↓
  Dashboard / UI              Reorder Point





  demand-forecasting/
│
├── data/
├── models/
│   ├── demand_classifier.pkl
│   └── quantity_model.pkl
│
├── src/
│   ├── data/
│   ├── features/
│   ├── models/
│   │   └── inference.py
│   ├── inventory/
│   │   └── optimizer.py
│   └── api/
│       └── main.py
│
├── notebooks/
│   ├── 01_data_understanding.ipynb
│   └── 02_model_training.ipynb
│
├── tests/
├── requirements.txt
├── Dockerfile
├── .gitignore
└── README.md