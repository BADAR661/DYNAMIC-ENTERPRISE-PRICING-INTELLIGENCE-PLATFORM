from pathlib import Path

import joblib
import pandas as pd
import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature

from backend.services.data_pipeline.feature_engineering import (
    prepare_forecasting_dataset,
)


ROOT = Path(__file__).resolve().parents[3]

DATA_PATH = ROOT / "data" / "processed" / "enriched_pricing_dataset.csv"
HOLIDAYS_PATH = ROOT / "data" / "raw" / "holidays.csv"
MODEL_PATH = ROOT / "models" / "forecast_model.joblib"
MLRUNS_PATH = ROOT / "mlruns"

MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
MLRUNS_PATH.mkdir(parents=True, exist_ok=True)


def _select_model():
    """
    Select the best available regression model.

    Priority:
    1. XGBoost
    2. LightGBM
    3. Scikit-learn HistGradientBoosting
    """

    try:
        from xgboost import XGBRegressor

        model = XGBRegressor(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=42,
            n_jobs=4,
            objective="reg:squarederror",
        )

        return model, "xgboost"

    except Exception:
        pass

    try:
        from lightgbm import LGBMRegressor

        model = LGBMRegressor(
            n_estimators=300,
            learning_rate=0.05,
            num_leaves=31,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=42,
            n_jobs=-1,
        )

        return model, "lightgbm"

    except Exception:
        pass

    from sklearn.ensemble import HistGradientBoostingRegressor

    model = HistGradientBoostingRegressor(
        learning_rate=0.05,
        max_depth=6,
        max_iter=300,
        random_state=42,
    )

    return model, "hist_gradient_boosting"


def train_baseline_model() -> None:

    # ---------------------------------------------------------
    # 1. Load data
    # ---------------------------------------------------------

    print("Loading dataset...")

    sales = pd.read_csv(DATA_PATH)
    holidays = pd.read_csv(HOLIDAYS_PATH)

    # ---------------------------------------------------------
    # 2. Prepare forecasting dataset
    # ---------------------------------------------------------

    print("Preparing forecasting dataset...")

    prepared = prepare_forecasting_dataset(
        sales,
        holidays,
    )

    # ---------------------------------------------------------
    # 3. Feature selection
    # ---------------------------------------------------------

    base_feature_columns = [
        "previous_sales",
        "lag_7_sales",
        "day_of_week",
        "month",
        "is_holiday",
        "price_trend",
        "recommended_price_trend",
        "day_of_week_sin",
        "day_of_week_cos",
        "month_sin",
        "month_cos",
        "week_of_year_sin",
        "week_of_year_cos",
    ]

    feature_columns = [
        column
        for column in base_feature_columns
        if column in prepared.columns
    ]

    X = prepared[feature_columns]
    y = prepared["target_sales"]

    if len(X) < 10:
        raise ValueError(
            "Not enough data to create a reliable train/test split."
        )

    # ---------------------------------------------------------
    # 4. Chronological train/test split
    # ---------------------------------------------------------

    # IMPORTANT:
    # Do NOT shuffle forecasting data.
    #
    # Earlier observations → training
    # Later observations   → testing

    split_index = int(len(X) * 0.8)

    X_train = X.iloc[:split_index].copy()
    X_test = X.iloc[split_index:].copy()

    y_train = y.iloc[:split_index].copy()
    y_test = y.iloc[split_index:].copy()

    print(f"Total rows: {len(X)}")
    print(f"Training rows: {len(X_train)}")
    print(f"Testing rows: {len(X_test)}")

    # ---------------------------------------------------------
    # 5. Select model
    # ---------------------------------------------------------

    model, model_type = _select_model()

    print(f"Training model: {model_type}")

    # ---------------------------------------------------------
    # 6. Train ONLY on training data
    # ---------------------------------------------------------

    model.fit(X_train, y_train)

    # ---------------------------------------------------------
    # 7. Predict unseen test data
    # ---------------------------------------------------------

    predictions = model.predict(X_test)

    # ---------------------------------------------------------
    # 8. Calculate proper test metrics
    # ---------------------------------------------------------

    errors = predictions - y_test.to_numpy()

    mse = float((errors ** 2).mean())

    rmse = float(mse ** 0.5)

    mae = float(abs(errors).mean())

    print("\nTest Metrics")
    print("-------------------------")
    print(f"MSE:  {mse:.6f}")
    print(f"RMSE: {rmse:.6f}")
    print(f"MAE:  {mae:.6f}")

    # ---------------------------------------------------------
    # 9. Save model artifact
    # ---------------------------------------------------------

    artifact = {
        "model": model,
        "features": feature_columns,
        "model_type": model_type,
    }

    joblib.dump(
        artifact,
        MODEL_PATH,
    )

    print(f"\nModel saved to:")
    print(MODEL_PATH)

    # ---------------------------------------------------------
    # 10. Configure MLflow
    # ---------------------------------------------------------

    tracking_uri = MLRUNS_PATH.resolve().as_uri()

    mlflow.set_tracking_uri(tracking_uri)

    mlflow.set_experiment(
        "dynamic-pricing-forecasting"
    )

    # ---------------------------------------------------------
    # 11. Create MLflow signature
    # ---------------------------------------------------------

    input_example = X_test.head(1)

    signature = infer_signature(
        X_test,
        predictions,
    )

    # ---------------------------------------------------------
    # 12. Start MLflow run
    # ---------------------------------------------------------

    with mlflow.start_run(
        run_name=f"train_{model_type}"
    ):

        # ---------------------------------------------
        # Parameters
        # ---------------------------------------------

        mlflow.log_param(
            "model_type",
            model_type,
        )

        mlflow.log_param(
            "feature_count",
            len(feature_columns),
        )

        mlflow.log_param(
            "total_rows",
            len(X),
        )

        mlflow.log_param(
            "training_rows",
            len(X_train),
        )

        mlflow.log_param(
            "testing_rows",
            len(X_test),
        )

        mlflow.log_param(
            "train_test_ratio",
            "80/20",
        )

        # ---------------------------------------------
        # XGBoost parameters
        # ---------------------------------------------

        if model_type == "xgboost":

            mlflow.log_params(
                {
                    "n_estimators": 300,
                    "learning_rate": 0.05,
                    "max_depth": 6,
                    "subsample": 0.9,
                    "colsample_bytree": 0.9,
                    "random_state": 42,
                }
            )

        # ---------------------------------------------
        # Metrics
        # ---------------------------------------------

        mlflow.log_metric(
            "test_mse",
            mse,
        )

        mlflow.log_metric(
            "test_rmse",
            rmse,
        )

        mlflow.log_metric(
            "test_mae",
            mae,
        )

        # ---------------------------------------------
        # Feature list
        # ---------------------------------------------

        mlflow.log_text(
            "\n".join(feature_columns),
            "feature_columns.txt",
        )

        # ---------------------------------------------
        # Log model with signature
        # ---------------------------------------------

        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            signature=signature,
            input_example=input_example,
        )

        # ---------------------------------------------
        # Log joblib model
        # ---------------------------------------------

        mlflow.log_artifact(
            str(MODEL_PATH),
            artifact_path="joblib",
        )

        print(
            f"MLflow run ID: {mlflow.active_run().info.run_id}"
        )

    print("\nTraining completed successfully.")


if __name__ == "__main__":
    train_baseline_model()