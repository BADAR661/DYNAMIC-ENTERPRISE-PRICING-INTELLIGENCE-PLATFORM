import pandas as pd

from backend.services.data_pipeline.feature_engineering import prepare_forecasting_dataset


def test_prepare_forecasting_dataset_creates_expected_features():
    sales = pd.DataFrame(
        [
            {"product_id": "P001", "sale_date": "2025-01-01", "quantity_sold": 10, "selling_price": 100, "recommended_price": 105, "discount_flag": 0},
            {"product_id": "P001", "sale_date": "2025-01-02", "quantity_sold": 12, "selling_price": 102, "recommended_price": 108, "discount_flag": 0},
        ]
    )
    holidays = pd.DataFrame({"holiday_date": ["2025-01-01"]})

    prepared = prepare_forecasting_dataset(sales, holidays)

    assert "previous_sales" in prepared.columns
    assert "day_of_week" in prepared.columns
    assert "month" in prepared.columns
    assert "is_holiday" in prepared.columns
    assert "price_trend" in prepared.columns
    assert "target_sales" in prepared.columns
    assert prepared["previous_sales"].notna().any()
