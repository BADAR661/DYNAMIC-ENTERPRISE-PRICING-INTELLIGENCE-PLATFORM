# Enterprise Dynamic Pricing Intelligence Platform

An end-to-end machine learning application for demand forecasting and dynamic pricing optimization. The platform combines a FastAPI service, Streamlit dashboard, XGBoost forecasting model, Redis caching, SQLAlchemy persistence, and explainable AI tooling.

## Architecture

```text
Browser
  |
  v
Streamlit :8501  --->  FastAPI :8000  --->  SQLite database
                             |
                             +------------> Redis :6379
```

The Docker Compose setup runs the dashboard, API, and Redis together. The trained model is included at `models/forecast_model.joblib`, while the local SQLite database and MLflow run history are generated at runtime and ignored by Git.

## Features

- Product selection using original catalog names from `data/raw/products.csv`
- Demand forecasting with an XGBoost model
- Pricing optimization and revenue simulation
- SHAP and LIME explainability endpoints
- Redis-backed response caching with an in-memory fallback
- SQLite persistence for products, sales, forecasts, and recommendations
- Docker Compose development and deployment workflow

## Run With Docker Compose

Requirements: Docker Desktop with Compose enabled.

```powershell
docker compose up --build
```

Open the dashboard at <http://localhost:8501>.

The API is available at <http://localhost:8000/docs>.

Stop all services with:

```powershell
docker compose down
```

## Streamlit Community Cloud

Streamlit Community Cloud hosts the dashboard only. The FastAPI backend must
be deployed separately on a reachable HTTPS host such as Render, Railway, or
another container platform.

After pushing the repository to GitHub:

1. Create a Streamlit Community Cloud app from the repository.
2. Set the main file to `frontend/app.py`.
3. Add the backend URL in the app secrets:

```toml
API_BASE_URL = "https://your-fastapi-service.example.com"
```

The dashboard reads this secret automatically. Do not use `127.0.0.1` or
`localhost` for the cloud deployment.

The Compose services are:

- `frontend`: Streamlit dashboard on port 8501
- `backend`: FastAPI API on port 8000
- `redis`: Redis cache on port 6379

## Local Development

Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Start the API and dashboard in separate terminals when running without Docker:

```powershell
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
streamlit run frontend/app.py
```

For local API access, the dashboard defaults to `http://127.0.0.1:8000`. Set `API_BASE_URL` when the API runs elsewhere.

## Data and Model

- Raw catalog and source files are in `data/raw/`.
- Processed feature data is in `data/processed/`.
- The committed model is `models/forecast_model.joblib`.
- To refresh the database from the catalog and processed data:

```powershell
python -m backend.database.seed_data
```

- To retrain the forecasting model:

```powershell
python backend/services/forecasting/train_model.py
```

Generated SQLite and MLflow files are intentionally excluded by `.gitignore`.

## Tests

```powershell
python -m pytest tests
```

## Repository Hygiene

Do not commit credentials, `.env` files, virtual environments, caches, local databases, or MLflow run output. Runtime configuration is supplied through environment variables such as `API_BASE_URL`, `REDIS_HOST`, and `REDIS_PORT`.
