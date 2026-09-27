**Real-Time Demand Forecasting & Inventory Optimization Platform**

**Version 1.0 is the final/frozen ML version.**

* V1.0 is based on the selected V12 experiment.
* Stage 1: XGBoost demand/no-demand classifier.
* Stage 2: XGBoost quantity regressor trained on `log1p(sales)`.
* Classifier threshold is fixed at **0.50**.
* Final model objects:

  * `demand_classifier_v1`
  * `quantity_model_v1`
  * `FEATURES_V1`
* Saved model files:

  * `models/demand_classifier_v1.pkl`
  * `models/quantity_model_v1.pkl`
  * `models/features_v1.pkl`
* ML experimentation and tuning are considered **finished for V1.0**.
* Future work should focus on building the application around the frozen model: inference pipeline, FastAPI, Docker, dashboard, testing, deployment, and documentation.
* Do not modify or retrain the V1.0 ML model unless explicitly starting **V2.0**.
* V12 refers to the experiment/version history. **V1.0 is the official final project model.**
