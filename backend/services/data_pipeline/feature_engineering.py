"""
Feature engineering utilities for the Enterprise Dynamic Pricing Intelligence Platform.

This module provides reusable functions for creating time-based features
from transactional date columns.
"""

import math

import numpy as np
import pandas as pd


def prepare_forecasting_dataset(
    sales_dataframe: pd.DataFrame,
    holidays_dataframe: pd.DataFrame,
    date_column: str = "sale_date",
    quantity_column: str = "quantity_sold",
    price_column: str = "selling_price",
    recommended_price_column: str = "recommended_price",
) -> pd.DataFrame:
    """Prepare a forecasting-ready dataset with lag, calendar, holiday, and price-trend features."""
    feature_dataframe = sales_dataframe.copy()

    if date_column not in feature_dataframe.columns:
        raise KeyError(f"Column '{date_column}' does not exist in the DataFrame.")

    feature_dataframe[date_column] = pd.to_datetime(feature_dataframe[date_column], errors="coerce")
    feature_dataframe = feature_dataframe.sort_values(["product_id", date_column]).reset_index(drop=True)

    feature_dataframe["previous_sales"] = feature_dataframe.groupby("product_id")[quantity_column].shift(1).fillna(0)
    feature_dataframe["lag_7_sales"] = feature_dataframe.groupby("product_id")[quantity_column].shift(7).fillna(0)
    feature_dataframe["day_of_week"] = feature_dataframe[date_column].dt.dayofweek
    feature_dataframe["month"] = feature_dataframe[date_column].dt.month
    feature_dataframe["week_of_year"] = feature_dataframe[date_column].dt.isocalendar().week.astype(int)
    feature_dataframe["day_of_year"] = feature_dataframe[date_column].dt.dayofyear
    feature_dataframe["day_of_week_sin"] = np.sin(2 * np.pi * feature_dataframe["day_of_week"] / 7)
    feature_dataframe["day_of_week_cos"] = np.cos(2 * np.pi * feature_dataframe["day_of_week"] / 7)
    feature_dataframe["month_sin"] = np.sin(2 * np.pi * feature_dataframe["month"] / 12)
    feature_dataframe["month_cos"] = np.cos(2 * np.pi * feature_dataframe["month"] / 12)
    feature_dataframe["week_of_year_sin"] = np.sin(2 * np.pi * feature_dataframe["week_of_year"] / 52)
    feature_dataframe["week_of_year_cos"] = np.cos(2 * np.pi * feature_dataframe["week_of_year"] / 52)
    feature_dataframe["is_holiday"] = 0

    if not holidays_dataframe.empty:
        holiday_dates = pd.to_datetime(holidays_dataframe.iloc[:, 0], errors="coerce").dropna().dt.normalize()
        feature_dataframe["is_holiday"] = feature_dataframe[date_column].dt.normalize().isin(holiday_dates).astype(int)

    feature_dataframe["price_trend"] = feature_dataframe.groupby("product_id")[price_column].pct_change().fillna(0)
    feature_dataframe["recommended_price_trend"] = feature_dataframe.groupby("product_id")[recommended_price_column].pct_change().fillna(0)
    feature_dataframe["target_sales"] = feature_dataframe.groupby("product_id")[quantity_column].shift(-1)

    return feature_dataframe.dropna(subset=["previous_sales", "target_sales"]).reset_index(drop=True)


def build_feature_vector(row: pd.Series, feature_columns: list[str]) -> list[float]:
    """Build a feature vector for a single observation using the saved feature list."""
    feature_values: list[float] = []
    for feature_name in feature_columns:
        if feature_name in row.index:
            value = row[feature_name]
        elif feature_name == "lag_7_sales":
            value = row.get("previous_sales", 0)
        elif feature_name == "day_of_week_sin" and "day_of_week" in row.index:
            value = math.sin(2 * math.pi * float(row["day_of_week"]) / 7)
        elif feature_name == "day_of_week_cos" and "day_of_week" in row.index:
            value = math.cos(2 * math.pi * float(row["day_of_week"]) / 7)
        elif feature_name == "month_sin" and "month" in row.index:
            value = math.sin(2 * math.pi * float(row["month"]) / 12)
        elif feature_name == "month_cos" and "month" in row.index:
            value = math.cos(2 * math.pi * float(row["month"]) / 12)
        elif feature_name == "week_of_year_sin" and "week_of_year" in row.index:
            value = math.sin(2 * math.pi * float(row["week_of_year"]) / 52)
        elif feature_name == "week_of_year_cos" and "week_of_year" in row.index:
            value = math.cos(2 * math.pi * float(row["week_of_year"]) / 52)
        else:
            value = 0.0
        feature_values.append(float(value))
    return feature_values


def create_time_features(
    dataframe: pd.DataFrame,
    date_column: str,
) -> pd.DataFrame:
    """
    Create time-based features from a datetime column.

    Features created:
        - year
        - month
        - day
        - day_of_week
        - is_weekend

    Args:
        dataframe: The pandas DataFrame containing the date column.
        date_column: The name of the datetime column.

    Returns:
        pd.DataFrame: A copy of the DataFrame with new time features.

    Raises:
        KeyError: If the specified date column does not exist.
    """

    feature_dataframe = dataframe.copy()

    if date_column not in feature_dataframe.columns:
        raise KeyError(
            f"Column '{date_column}' does not exist in the DataFrame."
        )

    if not pd.api.types.is_datetime64_any_dtype(
        feature_dataframe[date_column]
    ):
        feature_dataframe[date_column] = pd.to_datetime(
            feature_dataframe[date_column],
            errors="coerce",
        )

    feature_dataframe["year"] = feature_dataframe[date_column].dt.year
    feature_dataframe["month"] = feature_dataframe[date_column].dt.month
    feature_dataframe["day"] = feature_dataframe[date_column].dt.day
    feature_dataframe["day_of_week"] = (
        feature_dataframe[date_column].dt.dayofweek
    )
    feature_dataframe["is_weekend"] = (
        feature_dataframe[date_column].dt.dayofweek >= 5
    )

    return feature_dataframe
def add_holiday_feature(
    dataframe: pd.DataFrame,
    date_column: str,
    holidays_dataframe: pd.DataFrame,
    holiday_date_column: str,
) -> pd.DataFrame:
    """
    Add a boolean holiday indicator feature to the DataFrame.

    The function checks whether each date in the main DataFrame
    matches any holiday date in the holiday DataFrame.

    Args:
        dataframe: Main DataFrame containing transaction or sales data.
        date_column: Name of the date column in the main DataFrame.
        holidays_dataframe: DataFrame containing holiday dates.
        holiday_date_column: Name of the holiday date column.

    Returns:
        pd.DataFrame: A copy of the DataFrame with an `is_holiday` column.

    Raises:
        KeyError: If required columns do not exist.
    """

    feature_dataframe = dataframe.copy()
    holiday_data = holidays_dataframe.copy()

    if date_column not in feature_dataframe.columns:
        raise KeyError(
            f"Column '{date_column}' does not exist in the main DataFrame."
        )

    if holiday_date_column not in holiday_data.columns:
        raise KeyError(
            f"Column '{holiday_date_column}' does not exist in the holiday DataFrame."
        )

    feature_dataframe[date_column] = pd.to_datetime(
        feature_dataframe[date_column],
        errors="coerce",
    )

    holiday_data[holiday_date_column] = pd.to_datetime(
        holiday_data[holiday_date_column],
        errors="coerce",
    )

    holiday_dates = set(
        holiday_data[holiday_date_column]
        .dropna()
        .dt.normalize()
    )

    feature_dataframe["is_holiday"] = (
        feature_dataframe[date_column]
        .dt.normalize()
        .isin(holiday_dates)
    )

    return feature_dataframe
def calculate_price_elasticity(
    dataframe: pd.DataFrame,
    price_column: str,
    quantity_column: str,
) -> pd.DataFrame:
    """
    Calculate a basic price elasticity estimate using percentage changes.

    Price elasticity measures how sensitive quantity demanded is
    to changes in price.

    Formula:
        Price Elasticity =
        Percentage Change in Quantity /
        Percentage Change in Price

    Args:
        dataframe: DataFrame containing price and quantity data.
        price_column: Name of the price column.
        quantity_column: Name of the quantity column.

    Returns:
        pd.DataFrame: A copy of the DataFrame with a
        `price_elasticity` column.

    Raises:
        KeyError: If required columns do not exist.
    """

    feature_dataframe = dataframe.copy()

    if price_column not in feature_dataframe.columns:
        raise KeyError(
            f"Column '{price_column}' does not exist in the DataFrame."
        )

    if quantity_column not in feature_dataframe.columns:
        raise KeyError(
            f"Column '{quantity_column}' does not exist in the DataFrame."
        )

    price_change = feature_dataframe[price_column].pct_change()
    quantity_change = feature_dataframe[quantity_column].pct_change()

    feature_dataframe["price_elasticity"] = (
        quantity_change / price_change
    )

    return feature_dataframe
def calculate_inventory_turnover(
    dataframe: pd.DataFrame,
    quantity_column: str,
    inventory_column: str,
) -> pd.DataFrame:
    """
    Calculate an inventory turnover ratio.

    The inventory turnover ratio estimates how efficiently
    inventory is being sold.

    Formula:
        Inventory Turnover =
        Quantity Sold / Average Inventory

    Args:
        dataframe: DataFrame containing sales and inventory data.
        quantity_column: Name of the quantity sold column.
        inventory_column: Name of the inventory column.

    Returns:
        pd.DataFrame: A copy of the DataFrame with an
        `inventory_turnover` column.

    Raises:
        KeyError: If required columns do not exist.
    """

    feature_dataframe = dataframe.copy()

    if quantity_column not in feature_dataframe.columns:
        raise KeyError(
            f"Column '{quantity_column}' does not exist in the DataFrame."
        )

    if inventory_column not in feature_dataframe.columns:
        raise KeyError(
            f"Column '{inventory_column}' does not exist in the DataFrame."
        )

    feature_dataframe["inventory_turnover"] = (
        feature_dataframe[quantity_column]
        / feature_dataframe[inventory_column]
    )

    return feature_dataframe
def merge_sales_with_inventory(
    sales_dataframe: pd.DataFrame,
    inventory_dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Merge sales data with inventory data using product ID and date.

    Sales `sale_date` is matched with inventory `inventory_date`.

    Args:
        sales_dataframe: DataFrame containing sales information.
        inventory_dataframe: DataFrame containing inventory information.

    Returns:
        pd.DataFrame: A merged DataFrame containing sales and
        matching inventory data.

    Raises:
        KeyError: If required columns are missing.
    """

    required_sales_columns = {
        "product_id",
        "sale_date",
    }

    required_inventory_columns = {
        "product_id",
        "inventory_date",
    }

    missing_sales_columns = (
        required_sales_columns - set(sales_dataframe.columns)
    )

    missing_inventory_columns = (
        required_inventory_columns - set(inventory_dataframe.columns)
    )

    if missing_sales_columns:
        raise KeyError(
            f"Missing sales columns: {missing_sales_columns}"
        )

    if missing_inventory_columns:
        raise KeyError(
            f"Missing inventory columns: {missing_inventory_columns}"
        )

    sales_copy = sales_dataframe.copy()
    inventory_copy = inventory_dataframe.copy()

    sales_copy["sale_date"] = pd.to_datetime(
        sales_copy["sale_date"]
    )

    inventory_copy["inventory_date"] = pd.to_datetime(
        inventory_copy["inventory_date"]
    )

    merged_dataframe = sales_copy.merge(
        inventory_copy,
        left_on=["product_id", "sale_date"],
        right_on=["product_id", "inventory_date"],
        how="left",
    )

    return merged_dataframe
def fill_missing_inventory(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Fill missing average inventory values using
    product-specific median inventory.

    Args:
        dataframe: DataFrame containing product_id
            and average_inventory columns.

    Returns:
        pd.DataFrame: DataFrame with missing inventory
        values filled using product-level median.

    Raises:
        KeyError: If required columns are missing.
    """

    required_columns = {
        "product_id",
        "average_inventory",
    }

    missing_columns = (
        required_columns - set(dataframe.columns)
    )

    if missing_columns:
        raise KeyError(
            f"Missing required columns: {missing_columns}"
        )

    feature_dataframe = dataframe.copy()

    feature_dataframe["average_inventory"] = (
        feature_dataframe.groupby("product_id")[
            "average_inventory"
        ]
        .transform(
            lambda series: series.fillna(series.median())
        )
    )

    return feature_dataframe
def create_product_inventory_summary(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create product-level inventory turnover summary.

    The summary aggregates total quantity sold and average
    inventory for each product, then calculates inventory turnover.

    Args:
        dataframe: DataFrame containing product_id,
            quantity_sold, and average_inventory.

    Returns:
        pd.DataFrame: Product-level inventory summary.

    Raises:
        KeyError: If required columns are missing.
    """

    required_columns = {
        "product_id",
        "quantity_sold",
        "average_inventory",
    }

    missing_columns = (
        required_columns - set(dataframe.columns)
    )

    if missing_columns:
        raise KeyError(
            f"Missing required columns: {missing_columns}"
        )

    summary_dataframe = (
        dataframe
        .groupby("product_id", as_index=False)
        .agg(
            total_quantity_sold=("quantity_sold", "sum"),
            average_inventory=("average_inventory", "mean"),
        )
    )

    summary_dataframe["inventory_turnover"] = (
        summary_dataframe["total_quantity_sold"]
        / summary_dataframe["average_inventory"]
    )

    return summary_dataframe
def calculate_customer_lifetime_value(
    sales_dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate customer lifetime value from sales data.

    Customer lifetime value is calculated as the total revenue
    generated by each customer.

    Revenue for each transaction is calculated as:

        quantity_sold * selling_price

    Args:
        sales_dataframe: DataFrame containing customer_id,
            quantity_sold, and selling_price.

    Returns:
        pd.DataFrame: Customer-level lifetime value summary.

    Raises:
        KeyError: If required columns are missing.
    """

    required_columns = {
        "customer_id",
        "quantity_sold",
        "selling_price",
    }

    missing_columns = (
        required_columns - set(sales_dataframe.columns)
    )

    if missing_columns:
        raise KeyError(
            f"Missing required columns: {missing_columns}"
        )

    dataframe = sales_dataframe.copy()

    dataframe["revenue"] = (
        dataframe["quantity_sold"]
        * dataframe["selling_price"]
    )

    customer_lifetime_value = (
        dataframe
        .groupby("customer_id", as_index=False)
        .agg(
            total_revenue=("revenue", "sum"),
            total_orders=("customer_id", "count"),
        )
    )

    return customer_lifetime_value
def merge_customer_lifetime_value(
    customers_dataframe: pd.DataFrame,
    clv_dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Merge customer information with customer lifetime value.

    Args:
        customers_dataframe: DataFrame containing customer information.
        clv_dataframe: DataFrame containing customer lifetime value metrics.

    Returns:
        pd.DataFrame: Customer data enriched with CLV metrics.

    Raises:
        KeyError: If customer_id is missing from either DataFrame.
    """

    if "customer_id" not in customers_dataframe.columns:
        raise KeyError(
            "Column 'customer_id' does not exist in customer data."
        )

    if "customer_id" not in clv_dataframe.columns:
        raise KeyError(
            "Column 'customer_id' does not exist in CLV data."
        )

    enriched_customers = customers_dataframe.merge(
        clv_dataframe,
        on="customer_id",
        how="left",
    )

    return enriched_customers
def calculate_competitor_price_features(
    competitor_dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate competitor pricing features for each product.

    Features:
        - minimum competitor price
        - maximum competitor price
        - average competitor price
        - number of competitors

    Args:
        competitor_dataframe: DataFrame containing competitor pricing data.

    Returns:
        pd.DataFrame: Product-level competitor pricing features.

    Raises:
        KeyError: If required columns are missing.
    """

    required_columns = {
        "product_id",
        "competitor_name",
        "competitor_price",
    }

    missing_columns = required_columns - set(
        competitor_dataframe.columns
    )

    if missing_columns:
        raise KeyError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    competitor_features = (
        competitor_dataframe
        .groupby("product_id")
        .agg(
            min_competitor_price=(
                "competitor_price",
                "min",
            ),
            max_competitor_price=(
                "competitor_price",
                "max",
            ),
            average_competitor_price=(
                "competitor_price",
                "mean",
            ),
            competitor_count=(
                "competitor_name",
                "nunique",
            ),
        )
        .reset_index()
    )

    return competitor_features
def merge_sales_with_competitor_features(
    sales_dataframe: pd.DataFrame,
    competitor_features_dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Merge sales data with product-level competitor price features.

    Args:
        sales_dataframe: DataFrame containing sales information.
        competitor_features_dataframe: DataFrame containing
            product-level competitor pricing features.

    Returns:
        pd.DataFrame: Sales data enriched with competitor price features.

    Raises:
        KeyError: If product_id is missing from either DataFrame.
    """

    if "product_id" not in sales_dataframe.columns:
        raise KeyError(
            "Column 'product_id' does not exist in sales data."
        )

    if "product_id" not in competitor_features_dataframe.columns:
        raise KeyError(
            "Column 'product_id' does not exist in competitor features."
        )

    merged_dataframe = sales_dataframe.merge(
        competitor_features_dataframe,
        on="product_id",
        how="left",
    )

    return merged_dataframe
def calculate_price_difference_features(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate price difference between our selling price
    and the average competitor price.

    Features:
        - absolute price difference
        - percentage price difference
        - price position relative to competitors

    Args:
        dataframe: DataFrame containing selling price and
            average competitor price.

    Returns:
        pd.DataFrame: DataFrame with additional price difference features.

    Raises:
        KeyError: If required columns are missing.
    """

    required_columns = {
        "selling_price",
        "average_competitor_price",
    }

    missing_columns = required_columns - set(
        dataframe.columns
    )

    if missing_columns:
        raise KeyError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    result_dataframe = dataframe.copy()

    result_dataframe["price_difference"] = (
        result_dataframe["selling_price"]
        - result_dataframe["average_competitor_price"]
    )

    result_dataframe["price_difference_percentage"] = (
        result_dataframe["price_difference"]
        / result_dataframe["average_competitor_price"]
    ) * 100

    result_dataframe["price_position"] = (
        result_dataframe["selling_price"]
        / result_dataframe["average_competitor_price"]
    )

    return result_dataframe
def create_product_pricing_features(sales):
    """
    Create product-level pricing features from sales data.

    Features:
    - Average selling price
    - Total quantity sold
    - Total revenue
    """

    required_columns = [
        "product_id",
        "quantity_sold",
        "selling_price",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in sales.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    pricing_features = (
        sales.groupby("product_id")
        .agg(
            average_selling_price=(
                "selling_price",
                "mean",
            ),
            total_quantity_sold=(
                "quantity_sold",
                "sum",
            ),
            total_revenue=(
                "selling_price",
                lambda x: (
                    x
                    * sales.loc[
                        x.index,
                        "quantity_sold",
                    ]
                ).sum(),
            ),
        )
        .reset_index()
    )

    pricing_features[
        "average_selling_price"
    ] = pricing_features[
        "average_selling_price"
    ].round(2)

    pricing_features[
        "total_revenue"
    ] = pricing_features[
        "total_revenue"
    ].round(2)

    return pricing_features
def calculate_price_elasticity(sales):
    """
    Calculate a simple price elasticity estimate for each product.

    Elasticity = % Change in Quantity / % Change in Price
    """

    required_columns = [
        "product_id",
        "selling_price",
        "quantity_sold",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in sales.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    elasticity_results = []

    for product_id, group in sales.groupby("product_id"):

        group = group.sort_values("selling_price")

        if len(group) < 2:
            elasticity = 0.0

        else:
            avg_price = group["selling_price"].mean()
            avg_quantity = group["quantity_sold"].mean()

            price_change = (
                group["selling_price"].max()
                - group["selling_price"].min()
            )

            quantity_change = (
                group["quantity_sold"].max()
                - group["quantity_sold"].min()
            )

            if avg_price == 0 or avg_quantity == 0:
                elasticity = 0.0
            else:
                elasticity = (
                    (quantity_change / avg_quantity)
                    /
                    (price_change / avg_price)
                )

        elasticity_results.append(
            {
                "product_id": product_id,
                "price_elasticity": round(elasticity, 2),
            }
        )

    return pd.DataFrame(elasticity_results)
def calculate_average_competitor_price(competitor_prices):
    """
    Calculate the average competitor price for each product.
    """

    required_columns = [
        "product_id",
        "competitor_price",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in competitor_prices.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    average_prices = (
        competitor_prices
        .groupby("product_id")
        .agg(
            average_competitor_price=(
                "competitor_price",
                "mean",
            )
        )
        .reset_index()
    )

    average_prices[
        "average_competitor_price"
    ] = average_prices[
        "average_competitor_price"
    ].round(2)

    return average_prices