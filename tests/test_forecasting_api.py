from pathlib import Path
import joblib
from fastapi.testclient import TestClient

from backend.main import app
from backend.api import forecasting


class DummyModel:
    def predict(self, X):
        return [3.5]


def test_forecast_endpoint_returns_prediction(tmp_path, monkeypatch):
    artifact_path = tmp_path / "forecast_model.joblib"
    joblib.dump({"model": DummyModel(), "features": ["previous_sales", "day_of_week", "month", "is_holiday", "price_trend", "recommended_price_trend"], "model_type": "dummy"}, artifact_path)

    monkeypatch.setattr(forecasting, "MODEL_PATH", artifact_path)
    monkeypatch.setattr(forecasting, "DATA_PATH", Path("data/processed/enriched_pricing_dataset.csv"))
    monkeypatch.setattr(forecasting, "HOLIDAYS_PATH", Path("data/raw/holidays.csv"))

    client = TestClient(app)
    response = client.post(
        "/forecast",
        json={
            "product_id": "P001",
            "days_ahead": 7,
            "previous_sales": 10,
            "day_of_week": 2,
            "month": 8,
            "is_holiday": 0,
            "price_trend": 0.01,
            "recommended_price_trend": 0.02,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["predicted_demand"] == 3.5
    assert payload["product_id"] == "P001"
