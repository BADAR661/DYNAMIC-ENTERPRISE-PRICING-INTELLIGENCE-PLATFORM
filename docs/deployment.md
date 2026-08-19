# Deployment Guide

## Local development

1. Create and activate the project environment.
2. Install project dependencies.
3. Start the FastAPI backend:

```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

4. Start the Streamlit dashboard:

```bash
streamlit run frontend/app.py
```

5. Train or refresh the forecasting model:

```bash
python backend/services/forecasting/train_model.py
```

## Redis cache setup

A Redis instance is optional but recommended for shared caching. If Redis is available locally:

```bash
redis-server
```

The app automatically falls back to an in-memory cache when Redis is unavailable.

## MLflow tracking

To enable experiment tracking:

```bash
pip install mlflow
```

Then run the training script again. MLflow logs are stored under the `mlruns/` directory.

## Docker Compose deployment

Run the backend, dashboard, and Redis together:

```bash
docker compose up --build
```

Open the dashboard at `http://localhost:8501` and the API documentation at
`http://localhost:8000/docs`.

Stop the stack with:

```bash
docker compose down
```

## Production considerations

- use a real Redis server instead of the in-memory fallback
- configure environment variables for the deployment host and app metadata
- use a proper model registry and monitoring workflow for MLflow
- keep the dashboard and API behind a reverse proxy or production WSGI server
