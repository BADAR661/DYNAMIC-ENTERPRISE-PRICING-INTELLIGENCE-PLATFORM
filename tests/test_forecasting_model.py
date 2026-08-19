from pathlib import Path
import joblib

from backend.services.forecasting import train_model


def test_training_pipeline_saves_model_artifact_with_metadata(tmp_path, monkeypatch):
    root = Path(__file__).resolve().parents[1]
    data_path = root / "data" / "processed" / "enriched_pricing_dataset.csv"
    holidays_path = root / "data" / "raw" / "holidays.csv"
    model_path = tmp_path / "forecast_model.joblib"

    monkeypatch.setattr(train_model, "DATA_PATH", data_path)
    monkeypatch.setattr(train_model, "HOLIDAYS_PATH", holidays_path)
    monkeypatch.setattr(train_model, "MODEL_PATH", model_path)

    train_model.train_baseline_model()

    assert model_path.exists()
    artifact = joblib.load(model_path)
    assert "model" in artifact
    assert "features" in artifact
    assert "model_type" in artifact
    assert artifact["model_type"] in {"xgboost", "hist_gradient_boosting", "gradient_boosting"}
    assert any(feature.startswith("seasonal") or feature.endswith("sin") or feature.endswith("cos") for feature in artifact["features"])
