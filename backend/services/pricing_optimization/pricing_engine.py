import pandas as pd


def calculate_base_price(
    current_price: float,
    average_competitor_price: float,
    inventory_turnover: float,
    price_elasticity: float,
) -> float:
    """
    Calculate a recommended base price using
    current price, competitor price, inventory turnover,
    and price elasticity.
    """

    if current_price <= 0:
        raise ValueError(
            "Current price must be greater than zero."
        )

    if average_competitor_price <= 0:
        raise ValueError(
            "Average competitor price must be greater than zero."
        )

    if inventory_turnover < 0:
        raise ValueError(
            "Inventory turnover cannot be negative."
        )

    # Start with the current selling price.
    recommended_price = current_price

    # Adjust price toward the competitor market level.
    competitor_adjustment = (
        average_competitor_price - current_price
    ) * 0.30

    recommended_price += competitor_adjustment

    # If inventory turnover is low,
    # reduce price slightly to encourage sales.
    if inventory_turnover < 0.15:
        recommended_price *= 0.97

    # If inventory turnover is high,
    # increase price slightly because demand is stronger.
    elif inventory_turnover > 0.20:
        recommended_price *= 1.03

    # Apply elasticity adjustment.
    if price_elasticity < -1:
        recommended_price *= 0.98

    elif price_elasticity > -1:
        recommended_price *= 1.02

    return round(recommended_price, 2)
def calculate_discount_price(
    base_price: float,
    discount_percentage: float,
) -> float:
    """
    Calculate the final price after applying a discount.
    """

    if base_price <= 0:
        raise ValueError(
            "Base price must be greater than zero."
        )

    if discount_percentage < 0 or discount_percentage > 100:
        raise ValueError(
            "Discount percentage must be between 0 and 100."
        )

    discount_amount = (
        base_price * discount_percentage / 100
    )

    discounted_price = (
        base_price - discount_amount
    )

    return round(discounted_price, 2)
def calculate_peak_hour_price(
    base_price: float,
    is_peak_hour: bool,
    peak_multiplier: float = 1.10,
) -> float:
    """
    Calculate price based on peak-hour demand.
    """

    if base_price <= 0:
        raise ValueError(
            "Base price must be greater than zero."
        )

    if peak_multiplier <= 0:
        raise ValueError(
            "Peak multiplier must be greater than zero."
        )

    if is_peak_hour:
        recommended_price = (
            base_price * peak_multiplier
        )
    else:
        recommended_price = base_price

    return round(recommended_price, 2)
def calculate_bundle_price(
    product_prices: list[float],
    bundle_discount_percentage: float,
) -> float:
    """
    Calculate the final bundle price after applying
    a discount to the total price of multiple products.
    """

    if not product_prices:
        raise ValueError(
            "Product prices list cannot be empty."
        )

    if any(price <= 0 for price in product_prices):
        raise ValueError(
            "All product prices must be greater than zero."
        )

    if (
        bundle_discount_percentage < 0
        or bundle_discount_percentage > 100
    ):
        raise ValueError(
            "Bundle discount percentage must be between 0 and 100."
        )

    total_price = sum(product_prices)

    discount_amount = (
        total_price
        * bundle_discount_percentage
        / 100
    )

    bundle_price = (
        total_price - discount_amount
    )

    return round(bundle_price, 2)
def simulate_revenue_impact(
    price: float,
    expected_quantity: int,
    cost_per_unit: float,
) -> dict:
    """
    Simulate expected revenue, total cost, and profit
    for a given price and expected sales quantity.
    """

    if price <= 0:
        raise ValueError(
            "Price must be greater than zero."
        )

    if expected_quantity < 0:
        raise ValueError(
            "Expected quantity cannot be negative."
        )

    if cost_per_unit < 0:
        raise ValueError(
            "Cost per unit cannot be negative."
        )

    expected_revenue = (
        price * expected_quantity
    )

    total_cost = (
        cost_per_unit * expected_quantity
    )

    expected_profit = (
        expected_revenue - total_cost
    )

    profit_margin = (
        (expected_profit / expected_revenue) * 100
        if expected_revenue > 0
        else 0
    )

    return {
        "price": round(price, 2),
        "expected_quantity": expected_quantity,
        "expected_revenue": round(expected_revenue, 2),
        "total_cost": round(total_cost, 2),
        "expected_profit": round(expected_profit, 2),
        "profit_margin_percentage": round(
            profit_margin, 2
        ),
    }
def optimize_price(
    pricing_strategy: str,
    base_price: float,
    discount_percentage: float = 0.0,
    is_peak_hour: bool = False,
    peak_multiplier: float = 1.10,
    bundle_product_prices: list[float] | None = None,
    bundle_discount_percentage: float = 0.0,
) -> float:
    """
    Select and apply a pricing strategy
    to calculate the final optimized price.
    """

    if base_price <= 0:
        raise ValueError(
            "Base price must be greater than zero."
        )

    strategy = pricing_strategy.lower().strip()

    if strategy == "base":
        return round(base_price, 2)

    elif strategy == "discount":
        return calculate_discount_price(
            base_price=base_price,
            discount_percentage=discount_percentage,
        )

    elif strategy == "peak":
        return calculate_peak_hour_price(
            base_price=base_price,
            is_peak_hour=is_peak_hour,
            peak_multiplier=peak_multiplier,
        )

    elif strategy == "bundle":
        if not bundle_product_prices:
            raise ValueError(
                "Bundle product prices are required "
                "for bundle pricing."
            )

        return calculate_bundle_price(
            product_prices=bundle_product_prices,
            bundle_discount_percentage=bundle_discount_percentage,
        )

    else:
        raise ValueError(
            "Invalid pricing strategy. "
            "Use: base, discount, peak, or bundle."
        )