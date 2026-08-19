from backend.api.dashboard import build_dashboard_summary, get_alerts


def test_build_dashboard_summary_returns_alerts_and_status():
    summary = build_dashboard_summary(
        forecast_status="ready",
        predicted_demand=140,
        current_price=100.0,
        recommended_price=118.0,
        inventory_level=32,
    )

    assert summary["forecast_status"] == "ready"
    assert summary["alert_level"] in {"low", "medium", "high"}
    assert "alerts" in summary
    assert isinstance(summary["alerts"], list)


def test_get_alerts_raises_risk_for_stockout_and_overpricing():
    alerts = get_alerts(
        predicted_demand=180,
        current_price=120.0,
        recommended_price=90.0,
        inventory_level=15,
    )

    labels = {alert["type"] for alert in alerts}
    assert "stockout_risk" in labels
    assert "overpriced" in labels
