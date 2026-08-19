from __future__ import annotations

from typing import List, Optional

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    current_price: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), server_default=func.now())

    sales: Mapped[List["Sale"]] = relationship("Sale", back_populates="product", cascade="all, delete-orphan")
    inventory: Mapped[List["Inventory"]] = relationship("Inventory", back_populates="product", cascade="all, delete-orphan")
    pricing_history: Mapped[List["PricingHistory"]] = relationship("PricingHistory", back_populates="product", cascade="all, delete-orphan")
    forecast_results: Mapped[List["ForecastResult"]] = relationship("ForecastResult", back_populates="product", cascade="all, delete-orphan")
    price_recommendations: Mapped[List["PriceRecommendation"]] = relationship("PriceRecommendation", back_populates="product", cascade="all, delete-orphan")


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[str] = mapped_column(String(64), ForeignKey("products.product_id"), index=True, nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    sale_price: Mapped[float] = mapped_column(Float, nullable=False)
    sale_date: Mapped[Date] = mapped_column(Date, index=True, nullable=False)

    product: Mapped[Product] = relationship("Product", back_populates="sales")


class Inventory(Base):
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[str] = mapped_column(String(64), ForeignKey("products.product_id"), index=True, nullable=False)
    quantity_on_hand: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    warehouse_location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    product: Mapped[Product] = relationship("Product", back_populates="inventory")


class PricingHistory(Base):
    __tablename__ = "pricing_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[str] = mapped_column(String(64), ForeignKey("products.product_id"), index=True, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    start_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    end_date: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    product: Mapped[Product] = relationship("Product", back_populates="pricing_history")


class ForecastResult(Base):
    __tablename__ = "forecast_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[str] = mapped_column(String(64), ForeignKey("products.product_id"), index=True, nullable=False)
    forecast_date: Mapped[Date] = mapped_column(Date, index=True, nullable=False)
    predicted_demand: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    days_ahead: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    product: Mapped[Product] = relationship("Product", back_populates="forecast_results")


class PriceRecommendation(Base):
    __tablename__ = "price_recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[str] = mapped_column(String(64), ForeignKey("products.product_id"), index=True, nullable=False)
    recommended_price: Mapped[float] = mapped_column(Float, nullable=False)
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    generated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    product: Mapped[Product] = relationship("Product", back_populates="price_recommendations")


