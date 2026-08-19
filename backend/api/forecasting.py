from datetime import date, timedelta
from pathlib import Path

import joblib
import pandas as pd
from fastapi import APIRouter
from pydantic import BaseModel, Field
from sqlalchemy import select

from backend.cache import get_cache, make_cache_key, set_cache
from backend.database.database import SessionLocal
from backend.database.models import (
    ForecastResult,
    PriceRecommendation,
    Product,
)
from backend.services.data_pipeline.feature_engineering import (
    build_feature_vector,
    prepare_forecasting_dataset,
)


router = APIRouter(tags=["Forecasting"])


# ============================================================
# PATHS
# ============================================================

MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "models"
    / "forecast_model.joblib"
)

DATA_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "processed"
    / "enriched_pricing_dataset.csv"
)

HOLIDAYS_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "raw"
    / "holidays.csv"
)

MLRUNS_PATH = (
    Path(__file__).resolve().parents[2]
    / "mlruns"
)


# ============================================================
# REQUEST MODEL
# ============================================================

class ForecastRequest(BaseModel):

    product_id: str = Field(
        ...,
        description="Product identifier for the forecast",
    )

    days_ahead: int = Field(
        default=7,
        ge=1,
        le=90,
        description="Forecast horizon in days",
    )

    previous_sales: float = Field(
        default=0.0,
        description="Most recent observed quantity",
    )

    day_of_week: int = Field(
        default=0,
        ge=0,
        le=6,
        description="Day of week encoded as 0-6",
    )

    month: int = Field(
        default=1,
        ge=1,
        le=12,
        description="Month of year",
    )

    is_holiday: int = Field(
        default=0,
        ge=0,
        le=1,
        description="Holiday indicator",
    )

    price_trend: float = Field(
        default=0.0,
        description="Price trend over the last step",
    )

    recommended_price_trend: float = Field(
        default=0.0,
        description="Recommended price trend over the last step",
    )

    lag_7_sales: float = Field(
        default=0.0,
        description="Sales from seven periods ago",
    )

    current_price: float = Field(
        default=0.0,
        ge=0,
        description="Current product price",
    )


# ============================================================
# HEALTH
# ============================================================

@router.get("/health")
def forecasting_health() -> dict[str, str]:

    return {
        "status": "forecasting service ready"
    }


# ============================================================
# GET PRODUCT INFORMATION
# ============================================================

@router.get("/product/{product_id}")
def get_product(product_id: str) -> dict[str, object]:

    db = SessionLocal()

    try:

        product = db.scalar(
            select(Product).where(
                Product.product_id == product_id
            )
        )

        if product is None:

            return {
                "status": "product_not_found",
                "message": (
                    f"Product {product_id} "
                    "does not exist in the database."
                ),
            }

        return {
            "status": "success",
            "product_id": product.product_id,
            "name": product.name,
            "category": product.category,
            "current_price": product.current_price,
        }

    finally:

        db.close()


# ============================================================
# GET ALL PRODUCTS
# ============================================================

@router.get("/products")
def get_products() -> dict[str, object]:

    db = SessionLocal()

    try:

        products = db.scalars(
            select(Product).order_by(
                Product.product_id
            )
        ).all()

        return {
            "status": "success",
            "products": [
                {
                    "product_id": product.product_id,
                    "name": product.name,
                    "category": product.category,
                    "current_price": product.current_price,
                }
                for product in products
            ],
        }

    finally:

        db.close()


# ============================================================
# MAIN FORECAST ENDPOINT
# ============================================================

@router.post("/forecast")
def create_forecast(
    request: ForecastRequest,
) -> dict[str, object]:

    # ========================================================
    # 1. CHECK MODEL
    # ========================================================

    if not MODEL_PATH.exists():

        return {
            "status": "model_not_trained",
            "message": (
                "Train the model first and save it to "
                "models/forecast_model.joblib"
            ),
        }

    # ========================================================
    # 2. CACHE
    # ========================================================

    cache_key = make_cache_key(
        "forecast",
        request.model_dump(),
    )

    cached_result = get_cache(cache_key)

    if cached_result is not None:

        return cached_result

    # ========================================================
    # 3. DATABASE
    # ========================================================

    db = SessionLocal()

    try:

        product = db.scalar(
            select(Product).where(
                Product.product_id == request.product_id
            )
        )

        if product is None:

            return {
                "status": "product_not_found",
                "message": (
                    f"Product {request.product_id} "
                    "does not exist in the database."
                ),
            }

        # ====================================================
        # 4. LOAD MODEL
        # ====================================================

        artifact = joblib.load(
            MODEL_PATH
        )

        model = artifact["model"]

        feature_columns = artifact.get(
            "features",
            [
                "previous_sales",
                "day_of_week",
                "month",
                "is_holiday",
                "price_trend",
                "recommended_price_trend",
            ],
        )

        # ====================================================
        # 5. USE DATABASE PRICE IF FRONTEND DOES NOT PROVIDE IT
        # ====================================================

        current_price = request.current_price

        if current_price <= 0:

            current_price = product.current_price

        # ====================================================
        # 6. BUILD INPUT ROW
        # ====================================================

        row = pd.Series(
            {
                "product_id": request.product_id,

                "previous_sales":
                    request.previous_sales,

                "day_of_week":
                    request.day_of_week,

                "month":
                    request.month,

                "is_holiday":
                    request.is_holiday,

                "price_trend":
                    request.price_trend,

                "recommended_price_trend":
                    request.recommended_price_trend,

                "lag_7_sales":
                    request.lag_7_sales,
            }
        )

        # ====================================================
        # 7. BUILD FEATURES
        # ====================================================

        features = [
            build_feature_vector(
                row,
                feature_columns,
            )
        ]

        # ====================================================
        # 8. PREDICT
        # ====================================================

        prediction = max(
            0.0,
            round(
                float(
                    model.predict(features)[0]
                ),
                2,
            ),
        )

        # ====================================================
        # 9. RECOMMENDED PRICE
        # ====================================================

        recommended_price = None

        baseline_sales = max(
            request.previous_sales,
            1,
        )

        demand_gap = max(
            -0.15,
            min(
                0.15,
                (
                    prediction
                    - baseline_sales
                )
                / baseline_sales,
            ),
        )

        recommended_price = round(
            current_price
            * (1 + demand_gap),
            2,
        )

        # ====================================================
        # 10. FORECAST DATE
        # ====================================================

        forecast_date = (
            date.today()
            + timedelta(
                days=request.days_ahead
            )
        )

        # ====================================================
        # 11. SAVE FORECAST
        # ====================================================

        forecast_result = ForecastResult(
            product_id=request.product_id,
            forecast_date=forecast_date,
            predicted_demand=prediction,
            confidence=None,
            days_ahead=request.days_ahead,
        )

        db.add(
            forecast_result
        )

        # ====================================================
        # 12. SAVE PRICE RECOMMENDATION
        # ====================================================

        price_recommendation = PriceRecommendation(
            product_id=request.product_id,
            recommended_price=recommended_price,
            score=None,
            note=(
                "Generated from forecasted demand "
                "and current product price."
            ),
        )

        db.add(
            price_recommendation
        )

        db.commit()

        # ====================================================
        # 13. MLFLOW
        # ====================================================

        try:

            import mlflow

            MLRUNS_PATH.mkdir(
                parents=True,
                exist_ok=True,
            )

            tracking_uri = (
                MLRUNS_PATH
                .as_posix()
                .replace("\\", "/")
            )

            mlflow.set_tracking_uri(
                f"file:///{tracking_uri}"
            )

            mlflow.set_experiment(
                "dynamic-pricing-forecasting"
            )

            with mlflow.start_run(
                run_name=(
                    f"forecast_"
                    f"{request.product_id}"
                )
            ):

                mlflow.log_param(
                    "product_id",
                    request.product_id,
                )

                mlflow.log_param(
                    "product_name",
                    product.name,
                )

                mlflow.log_param(
                    "days_ahead",
                    request.days_ahead,
                )

                mlflow.log_metric(
                    "predicted_demand",
                    prediction,
                )

                mlflow.log_metric(
                    "recommended_price",
                    recommended_price,
                )

                mlflow.log_artifact(
                    str(MODEL_PATH)
                )

        except Exception:

            # MLflow must never break forecasting.
            pass

        # ====================================================
        # 14. RESPONSE
        # ====================================================

        payload = {

            "status":
                "success",

            "product_id":
                product.product_id,

            "product_name":
                product.name,

            "category":
                product.category,

            "days_ahead":
                request.days_ahead,

            "forecast_date":
                forecast_date.isoformat(),

            "predicted_demand":
                prediction,

            "current_price":
                current_price,

            "recommended_price":
                recommended_price,

            "source":
                artifact.get(
                    "model_type",
                    "XGBoost",
                ),

            "database_saved":
                True,

            "feature_values": {
                name: float(value)
                for name, value in zip(
                    feature_columns,
                    features[0],
                )
            },
        }

        # ====================================================
        # 15. CACHE
        # ====================================================

        set_cache(
            cache_key,
            payload,
        )

        return payload

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()


# ============================================================
# DATASET-BASED PREDICTION
# ============================================================

@router.post("/predict")
def predict_forecast(
    product_id: str,
    days_ahead: int = 7,
) -> dict[str, object]:

    if not MODEL_PATH.exists():

        return {
            "status": "model_not_trained",
            "message": (
                "Train the model first."
            ),
        }

    if not DATA_PATH.exists():

        return {
            "status": "data_missing",
            "message": (
                "Processed dataset not found"
            ),
        }

    # ========================================================
    # LOAD DATA
    # ========================================================

    sales = pd.read_csv(
        DATA_PATH
    )

    holidays = pd.read_csv(
        HOLIDAYS_PATH
    )

    prepared = prepare_forecasting_dataset(
        sales,
        holidays,
    )

    product_data = prepared[
        prepared["product_id"] == product_id
    ].tail(1)

    if product_data.empty:

        return {
            "status": "no_data",
            "message": (
                f"No sales data for product "
                f"{product_id}"
            ),
        }

    # ========================================================
    # DATABASE PRODUCT
    # ========================================================

    db = SessionLocal()

    try:

        product = db.scalar(
            select(Product).where(
                Product.product_id == product_id
            )
        )

        if product is None:

            return {
                "status": "product_not_found",
                "message": (
                    f"Product {product_id} "
                    "does not exist."
                ),
            }

        # ====================================================
        # MODEL
        # ====================================================

        artifact = joblib.load(
            MODEL_PATH
        )

        model = artifact["model"]

        feature_columns = artifact.get(
            "features",
            [
                "previous_sales",
                "day_of_week",
                "month",
                "is_holiday",
                "price_trend",
                "recommended_price_trend",
            ],
        )

        row = product_data.iloc[0]

        features = [
            build_feature_vector(
                row,
                feature_columns,
            )
        ]

        prediction = max(
            0.0,
            round(
                float(
                    model.predict(features)[0]
                ),
                2,
            ),
        )

        forecast_date = (
            date.today()
            + timedelta(days=days_ahead)
        )

        return {

            "status":
                "success",

            "product_id":
                product.product_id,

            "product_name":
                product.name,

            "category":
                product.category,

            "current_price":
                product.current_price,

            "days_ahead":
                days_ahead,

            "forecast_date":
                forecast_date.isoformat(),

            "predicted_demand":
                prediction,

            "source":
                artifact.get(
                    "model_type",
                    "XGBoost",
                ),

            "feature_values": {
                name: float(value)
                for name, value in zip(
                    feature_columns,
                    features[0],
                )
            },
        }

    finally:

        db.close()