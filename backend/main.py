from fastapi import FastAPI

from backend.config import settings
from backend.api.health import router as health_router
from backend.api.pricing import router as pricing_router
from backend.api.forecasting import router as forecasting_router
from backend.api.dashboard import router as dashboard_router
from backend.api.explainability import router as explainability_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)


@app.get("/")
def read_root() -> dict[str, str]:
    """Root endpoint confirming the API is running."""
    return {"message": "Enterprise Dynamic Pricing Intelligence Platform API is running."}


app.include_router(health_router)
app.include_router(pricing_router)
app.include_router(forecasting_router)
app.include_router(dashboard_router)
app.include_router(explainability_router)