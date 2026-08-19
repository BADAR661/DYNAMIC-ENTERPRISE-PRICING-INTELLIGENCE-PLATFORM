from pathlib import Path

import joblib
import pandas as pd
import numpy as np
from lime.lime_tabular import LimeTabularExplainer


ROOT = Path(__file__).resolve().parents[3]

MODEL_PATH = ROOT / "models" / "forecast_model.joblib"
DATA_PATH = ROOT / "data" / "processed" / "enriched_pricing_dataset.csv"
HOLIDAYS_PATH = ROOT / "data" / "raw" / "holidays.csv"


def explain_prediction(
    feature_values: dict[str, float],
) -> dict:

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "Forecast model not found. Train the model first."
        )

    artifact = joblib.load(MODEL_PATH)

    model = artifact["model"]
    feature_columns = artifact["features"]

    # ---------------------------------------------------------
    # Load training data
    # ---------------------------------------------------------

    sales = pd.read_csv(DATA_PATH)
    holidays = pd.read_csv(HOLIDAYS_PATH)

    from backend.services.data_pipeline.feature_engineering import (
        prepare_forecasting_dataset,
    )

    prepared = prepare_forecasting_dataset(
        sales,
        holidays,
    )

    # Keep exactly the features used by the model
    training_data = prepared[feature_columns].copy()

    # Fill missing values if any
    training_data = training_data.fillna(0)

    X_train = training_data.to_numpy(dtype=float)

    # ---------------------------------------------------------
    # Input observation
    # ---------------------------------------------------------

    input_values = np.array(
        [
            feature_values.get(column, 0.0)
            for column in feature_columns
        ],
        dtype=float,
    )

    input_data = pd.DataFrame(
        [input_values],
        columns=feature_columns,
    )

    prediction = float(
        model.predict(input_data)[0]
    )

    # ---------------------------------------------------------
    # Create LIME explainer
    # ---------------------------------------------------------

    explainer = LimeTabularExplainer(
        training_data=X_train,
        feature_names=feature_columns,
        mode="regression",
        discretize_continuous=True,
        random_state=42,
    )

    # ---------------------------------------------------------
    # Generate explanation
    # ---------------------------------------------------------

    explanation = explainer.explain_instance(
        input_values,
        model.predict,
        num_features=len(feature_columns),
    )

    feature_explanations = []

    for feature_name, weight in explanation.as_list():

        feature_explanations.append(
            {
                "feature": feature_name,
                "weight": round(float(weight), 6),
                "impact": (
                    "positive"
                    if weight > 0
                    else "negative"
                    if weight < 0
                    else "neutral"
                ),
            }
        )

    feature_explanations.sort(
        key=lambda item: abs(item["weight"]),
        reverse=True,
    )

    return {
        "prediction": round(prediction, 2),
        "features": feature_explanations,
    }