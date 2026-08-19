from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.services.explainability.shap_explainer import (
    explain_prediction as explain_shap_prediction,
)

from backend.services.explainability.lime_explainer import (
    explain_prediction as explain_lime_prediction,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/explainability",
    tags=["Explainability"],
)


# ============================================================
# EXPLAINABILITY REQUEST
# ============================================================

class ExplainabilityRequest(BaseModel):
    """
    Input features used by the forecasting model.

    These features must match the feature order and names
    stored inside forecast_model.joblib.
    """

    previous_sales: float = Field(
        default=0.0,
        description="Most recent observed sales quantity",
    )

    lag_7_sales: float = Field(
        default=0.0,
        description="Sales quantity from seven periods ago",
    )

    day_of_week: int = Field(
        default=0,
        ge=0,
        le=6,
        description="Day of week encoded from 0 to 6",
    )

    month: int = Field(
        default=1,
        ge=1,
        le=12,
        description="Month encoded from 1 to 12",
    )

    is_holiday: int = Field(
        default=0,
        ge=0,
        le=1,
        description="Holiday indicator",
    )

    price_trend: float = Field(
        default=0.0,
        description="Recent price trend",
    )

    recommended_price_trend: float = Field(
        default=0.0,
        description="Recent recommended price trend",
    )

    day_of_week_sin: float = Field(
        default=0.0,
        description="Cyclical sine encoding of day of week",
    )

    day_of_week_cos: float = Field(
        default=0.0,
        description="Cyclical cosine encoding of day of week",
    )

    month_sin: float = Field(
        default=0.0,
        description="Cyclical sine encoding of month",
    )

    month_cos: float = Field(
        default=0.0,
        description="Cyclical cosine encoding of month",
    )

    week_of_year_sin: float = Field(
        default=0.0,
        description="Cyclical sine encoding of week of year",
    )

    week_of_year_cos: float = Field(
        default=0.0,
        description="Cyclical cosine encoding of week of year",
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@router.get("/health")
def explainability_health() -> dict[str, str]:
    """
    Check whether the explainability service is available.
    """

    return {
        "status": "explainability service ready"
    }


# ============================================================
# SHAP EXPLANATION
# ============================================================

@router.post("/shap")
def shap_explanation(
    request: ExplainabilityRequest,
) -> dict[str, object]:
    """
    Generate a SHAP explanation for a single forecast.

    SHAP explains how each model feature contributes
    positively or negatively to the prediction.
    """

    try:

        feature_values = request.model_dump()

        result = explain_shap_prediction(
            feature_values
        )

        return {
            "status": "success",
            "method": "SHAP",
            **result,
        }

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"SHAP explanation failed: {error}",
        )


# ============================================================
# LIME EXPLANATION
# ============================================================

@router.post("/lime")
def lime_explanation(
    request: ExplainabilityRequest,
) -> dict[str, object]:
    """
    Generate a LIME explanation for a single forecast.

    LIME explains which features locally influence
    the model prediction.
    """

    try:

        feature_values = request.model_dump()

        result = explain_lime_prediction(
            feature_values
        )

        return {
            "status": "success",
            "method": "LIME",
            **result,
        }

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"LIME explanation failed: {error}",
        )