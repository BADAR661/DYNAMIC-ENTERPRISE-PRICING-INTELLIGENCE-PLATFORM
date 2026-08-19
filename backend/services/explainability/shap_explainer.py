from pathlib import Path

import joblib
import pandas as pd
import shap


ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = ROOT / "models" / "forecast_model.joblib"


def load_model_artifact():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "Forecast model not found. Train the model first."
        )

    return joblib.load(MODEL_PATH)


def explain_prediction(
    feature_values: dict[str, float],
) -> dict:
    """
    Generate SHAP explanation for a single forecast prediction.
    """

    artifact = load_model_artifact()

    model = artifact["model"]
    feature_columns = artifact["features"]

    # Build input dataframe in exactly the same
    # feature order used during model training.
    input_data = pd.DataFrame(
        [[
            feature_values.get(column, 0.0)
            for column in feature_columns
        ]],
        columns=feature_columns,
    )

    # Model prediction
    prediction = float(model.predict(input_data)[0])

    # TreeExplainer works directly with XGBoost
    explainer = shap.TreeExplainer(model)

    shap_values = explainer.shap_values(input_data)

    # SHAP may return ndarray or list depending on model/version.
    if isinstance(shap_values, list):
        shap_values = shap_values[0]

    shap_values = shap_values[0]

    explanation = []

    for feature_name, feature_value, shap_value in zip(
        feature_columns,
        input_data.iloc[0].tolist(),
        shap_values,
    ):
        explanation.append(
            {
                "feature": feature_name,
                "value": round(float(feature_value), 6),
                "shap_value": round(float(shap_value), 6),
                "impact": (
                    "positive"
                    if shap_value > 0
                    else "negative"
                    if shap_value < 0
                    else "neutral"
                ),
            }
        )

    # Most influential features first
    explanation.sort(
        key=lambda item: abs(item["shap_value"]),
        reverse=True,
    )

    return {
        "prediction": round(prediction, 2),
        "base_value": round(
            float(explainer.expected_value),
            2,
        ),
        "features": explanation,
    }