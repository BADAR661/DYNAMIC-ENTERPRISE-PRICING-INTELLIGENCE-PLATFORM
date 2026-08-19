# Member 2 Implementation Plan

## Goal
Build a simple forecasting + API + dashboard MVP for the dynamic pricing platform.

## Step 1: Prepare data
- Load the processed sales dataset from data/processed/enriched_pricing_dataset.csv
- Convert sale_date to datetime
- Aggregate sales by day or week
- Create basic features such as:
  - day of week
  - month
  - previous sales
  - price trend

## Step 2: Train a baseline forecasting model
Use a simple regression-based approach first.
- Train a model on historical sales features
- Predict next-period demand
- Save the model to models/forecast_model.joblib

## Step 3: Expose a forecasting API
Add an API endpoint in backend/api/forecasting.py and register it in backend/main.py.

Example endpoint:
- POST /forecast
- Input: product_id, days_ahead, optional region
- Output: predicted demand and recommended price

## Step 4: Add MLflow tracking
- Initialize an MLflow experiment
- Log the model, metrics, and parameters
- Save experiment metadata to mlruns/

## Step 5: Add Redis caching
- Cache repeated forecasting requests by request payload
- Return cached results when the same request is repeated

## Step 6: Build a dashboard
Create a simple dashboard using Streamlit or a lightweight HTML page.
Show:
- forecast chart
- current recommendations
- alerts

## Step 7: Add alerts
Create simple alert rules:
- high forecast => show warning
- low forecast => show caution

## Step 8: Document and run
- Document setup commands
- Run the API locally
- Run the dashboard locally
