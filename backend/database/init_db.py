from .database import engine, Base

# Ensure models are imported so their metadata is registered
from backend.database import models  # noqa: F401


def init_db() -> None:
    """Create all database tables for the application."""
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print(f"Initialized database and created tables in {engine.url}")
