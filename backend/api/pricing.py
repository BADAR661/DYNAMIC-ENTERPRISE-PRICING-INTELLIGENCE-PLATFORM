from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from backend.database.database import SessionLocal
from backend.database.models import (
    Product,
    PriceRecommendation,
    PricingHistory,
)

from backend.services.pricing_optimization.pricing_engine import (
    optimize_price,
    simulate_revenue_impact,
)


router = APIRouter(
    prefix="/pricing",
    tags=["Pricing"],
)


# ============================================================
# 1. PRICING OPTIMIZATION REQUEST
# ============================================================

class PricingRequest(BaseModel):
    product_id: str | None = Field(
        default=None,
        description="Product identifier",
    )

    pricing_strategy: str = Field(
        ...,
        description="Pricing strategy: base, discount, peak, or bundle",
    )

    base_price: float = Field(
        ...,
        gt=0,
        description="Base product price",
    )

    discount_percentage: float = Field(
        default=0.0,
        ge=0,
        le=100,
        description="Discount percentage",
    )

    is_peak_hour: bool = Field(
        default=False,
        description="Whether the current time is peak hour",
    )

    peak_multiplier: float = Field(
        default=1.10,
        gt=0,
        description="Peak hour price multiplier",
    )

    bundle_product_prices: list[float] | None = Field(
        default=None,
        description="Prices of products included in bundle",
    )

    bundle_discount_percentage: float = Field(
        default=0.0,
        ge=0,
        le=100,
        description="Bundle discount percentage",
    )


# ============================================================
# 2. OPTIMIZE PRICE
# ============================================================

@router.post("/optimize")
def optimize_pricing(
    request: PricingRequest,
) -> dict[str, object]:

    try:
        optimized_price = optimize_price(
            pricing_strategy=request.pricing_strategy,
            base_price=request.base_price,
            discount_percentage=request.discount_percentage,
            is_peak_hour=request.is_peak_hour,
            peak_multiplier=request.peak_multiplier,
            bundle_product_prices=request.bundle_product_prices,
            bundle_discount_percentage=request.bundle_discount_percentage,
        )

        return {
            "product_id": request.product_id,
            "pricing_strategy": request.pricing_strategy,
            "base_price": request.base_price,
            "optimized_price": optimized_price,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


# ============================================================
# 3. REVENUE SIMULATION REQUEST
# ============================================================

class RevenueSimulationRequest(BaseModel):
    price: float = Field(
        ...,
        gt=0,
        description="Product selling price",
    )

    expected_quantity: int = Field(
        ...,
        ge=0,
        description="Expected number of units sold",
    )

    cost_per_unit: float = Field(
        ...,
        ge=0,
        description="Cost per unit",
    )


# ============================================================
# 4. REVENUE SIMULATION
# ============================================================

@router.post("/simulate-revenue")
def simulate_revenue(
    request: RevenueSimulationRequest,
) -> dict[str, object]:

    try:
        return simulate_revenue_impact(
            price=request.price,
            expected_quantity=request.expected_quantity,
            cost_per_unit=request.cost_per_unit,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


# ============================================================
# 5. COMBINED PRICING SIMULATION REQUEST
# ============================================================

class PricingSimulationRequest(BaseModel):
    product_id: str = Field(
        ...,
        description="Product identifier",
    )

    pricing_strategy: str = Field(
        ...,
        description="Pricing strategy: base, discount, peak, or bundle",
    )

    base_price: float = Field(
        ...,
        gt=0,
    )

    expected_quantity: int = Field(
        ...,
        ge=0,
    )

    cost_per_unit: float = Field(
        ...,
        ge=0,
    )

    discount_percentage: float = Field(
        default=0.0,
        ge=0,
        le=100,
    )

    is_peak_hour: bool = Field(
        default=False,
    )

    peak_multiplier: float = Field(
        default=1.10,
        gt=0,
    )

    bundle_product_prices: list[float] | None = Field(
        default=None,
    )

    bundle_discount_percentage: float = Field(
        default=0.0,
        ge=0,
        le=100,
    )


# ============================================================
# 6. OPTIMIZE + SIMULATE + SAVE TO DATABASE
# ============================================================

@router.post("/optimize-and-simulate")
def optimize_and_simulate(
    request: PricingSimulationRequest,
) -> dict[str, object]:

    db = SessionLocal()

    try:

        # ----------------------------------------------------
        # Verify product exists
        # ----------------------------------------------------

        product = db.scalar(
            select(Product).where(
                Product.product_id == request.product_id
            )
        )

        if product is None:
            raise HTTPException(
                status_code=404,
                detail=f"Product {request.product_id} not found.",
            )

        # ----------------------------------------------------
        # Calculate optimized price
        # ----------------------------------------------------

        optimized_price = optimize_price(
            pricing_strategy=request.pricing_strategy,
            base_price=request.base_price,
            discount_percentage=request.discount_percentage,
            is_peak_hour=request.is_peak_hour,
            peak_multiplier=request.peak_multiplier,
            bundle_product_prices=request.bundle_product_prices,
            bundle_discount_percentage=request.bundle_discount_percentage,
        )

        # ----------------------------------------------------
        # Revenue simulation
        # ----------------------------------------------------

        simulation_result = simulate_revenue_impact(
            price=optimized_price,
            expected_quantity=request.expected_quantity,
            cost_per_unit=request.cost_per_unit,
        )

        # ----------------------------------------------------
        # Save price recommendation
        # ----------------------------------------------------

        recommendation = PriceRecommendation(
            product_id=request.product_id,
            recommended_price=optimized_price,
            score=None,
            note=(
                f"Strategy: {request.pricing_strategy}. "
                f"Expected quantity: {request.expected_quantity}."
            ),
        )

        db.add(recommendation)

        # ----------------------------------------------------
        # Save pricing history
        # ----------------------------------------------------

        pricing_history = PricingHistory(
            product_id=request.product_id,
            price=optimized_price,
            start_date=datetime.utcnow(),
            end_date=None,
            reason=(
                f"Pricing strategy: "
                f"{request.pricing_strategy}"
            ),
        )

        db.add(pricing_history)

        # ----------------------------------------------------
        # Update product current price
        # ----------------------------------------------------

        product.current_price = optimized_price

        db.commit()

        db.refresh(recommendation)
        db.refresh(pricing_history)

        # ----------------------------------------------------
        # Final response
        # ----------------------------------------------------

        return {
            "status": "success",
            "product_id": request.product_id,
            "pricing_strategy": request.pricing_strategy,
            "base_price": request.base_price,
            "optimized_price": optimized_price,
            "expected_quantity": request.expected_quantity,
            "cost_per_unit": request.cost_per_unit,
            "expected_revenue": simulation_result[
                "expected_revenue"
            ],
            "total_cost": simulation_result[
                "total_cost"
            ],
            "expected_profit": simulation_result[
                "expected_profit"
            ],
            "profit_margin_percentage": simulation_result[
                "profit_margin_percentage"
            ],
            "database_saved": True,
            "recommendation_id": recommendation.id,
            "pricing_history_id": pricing_history.id,
        }

    except HTTPException:
        db.rollback()
        raise

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Database pricing error: {str(error)}",
        )

    finally:
        db.close()


# ============================================================
# 7. GET PRODUCT RECOMMENDATIONS
# ============================================================

@router.get("/recommendations/{product_id}")
def get_recommendations(
    product_id: str,
) -> dict[str, object]:

    db = SessionLocal()

    try:

        product = db.scalar(
            select(Product).where(
                Product.product_id == product_id
            )
        )

        if product is None:
            raise HTTPException(
                status_code=404,
                detail=f"Product {product_id} not found.",
            )

        recommendations = db.scalars(
            select(PriceRecommendation)
            .where(
                PriceRecommendation.product_id == product_id
            )
            .order_by(
                PriceRecommendation.generated_at.desc()
            )
        ).all()

        return {
            "product_id": product_id,
            "current_price": product.current_price,
            "count": len(recommendations),
            "recommendations": [
                {
                    "id": recommendation.id,
                    "recommended_price": recommendation.recommended_price,
                    "score": recommendation.score,
                    "generated_at": recommendation.generated_at,
                    "note": recommendation.note,
                }
                for recommendation in recommendations
            ],
        }

    finally:
        db.close()


# ============================================================
# 8. GET PRICING HISTORY
# ============================================================

@router.get("/history/{product_id}")
def get_pricing_history(
    product_id: str,
) -> dict[str, object]:

    db = SessionLocal()

    try:

        product = db.scalar(
            select(Product).where(
                Product.product_id == product_id
            )
        )

        if product is None:
            raise HTTPException(
                status_code=404,
                detail=f"Product {product_id} not found.",
            )

        history = db.scalars(
            select(PricingHistory)
            .where(
                PricingHistory.product_id == product_id
            )
            .order_by(
                PricingHistory.start_date.desc()
            )
        ).all()

        return {
            "product_id": product_id,
            "count": len(history),
            "history": [
                {
                    "id": item.id,
                    "price": item.price,
                    "start_date": item.start_date,
                    "end_date": item.end_date,
                    "reason": item.reason,
                }
                for item in history
            ],
        }

    finally:
        db.close()