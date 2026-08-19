from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Project data directory and standardized DB filename
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DATABASE_PATH = DATA_DIR / "dynamic_pricing.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

# SQLAlchemy engine and session factory
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
