from fastapi import APIRouter

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_alerts(
    predicted_demand: float | int | None = None,
    current_price: float | None = None,
    recommended_price: float | None = None,
    inventory_level: float | int | None = None,
) -> list[dict[str, object]]:
    """Create a simple alert list based on demand, pricing, and stock levels."""
    alerts: list[dict[str, object]] = []

    if predicted_demand is not None and predicted_demand > 150:
        alerts.append(
            {
                "type": "high_demand",
                "severity": "high",
                "message": "Demand is above the normal threshold and pricing should be reviewed.",
            }
        )

    if inventory_level is not None and inventory_level < 20:
        alerts.append(
            {
                "type": "stockout_risk",
                "severity": "high",
                "message": "Inventory is low; a stockout risk is present for this product.",
            }
        )

    if current_price is not None and recommended_price is not None:
        if current_price > recommended_price * 1.05:
            alerts.append(
                {
                    "type": "overpriced",
                    "severity": "medium",
                    "message": "Current price is materially above the recommended price.",
                }
            )
        elif current_price < recommended_price * 0.95:
            alerts.append(
                {
                    "type": "underpriced",
                    "severity": "low",
                    "message": "Current price is below the recommended price. Consider tightening margins.",
                }
            )

    if not alerts:
        alerts.append(
            {
                "type": "stable",
                "severity": "low",
                "message": "Pricing and inventory are stable; no immediate action required.",
            }
        )

    return alerts


def build_dashboard_summary(
    forecast_status: str = "ready",
    predicted_demand: float | int | None = None,
    current_price: float | None = None,
    recommended_price: float | None = None,
    inventory_level: float | int | None = None,
) -> dict[str, object]:
    alerts = get_alerts(
        predicted_demand=predicted_demand,
        current_price=current_price,
        recommended_price=recommended_price,
        inventory_level=inventory_level,
    )

    severities = [alert["severity"] for alert in alerts]
    if "high" in severities:
        alert_level = "high"
        recommended_action = "Increase pricing discipline and protect inventory for the next sales window."
    elif "medium" in severities:
        alert_level = "medium"
        recommended_action = "Monitor the demand trend and adjust pricing before the next cycle."
    else:
        alert_level = "low"
        recommended_action = "Current pricing is stable; continue monitoring the forecast trend."

    return {
        "forecast_status": forecast_status,
        "alert_level": alert_level,
        "recommended_action": recommended_action,
        "alerts": alerts,
        "predicted_demand": predicted_demand,
        "current_price": current_price,
        "recommended_price": recommended_price,
        "inventory_level": inventory_level,
    }


@router.get("/summary")
def get_dashboard_summary() -> dict[str, object]:
    return build_dashboard_summary(
        forecast_status="ready",
        predicted_demand=140,
        current_price=100.0,
        recommended_price=118.0,
        inventory_level=32,
    )


@router.get("/alerts")
def get_alerts_summary() -> dict[str, object]:
    return {
        "alerts": get_alerts(
            predicted_demand=140,
            current_price=100.0,
            recommended_price=118.0,
            inventory_level=32,
        )
    }
