"""
Data ingestion utilities for the Enterprise Dynamic Pricing Intelligence Platform.

This module provides reusable, well-validated functions for loading raw data
into the pipeline. It currently supports CSV ingestion and is structured so
that additional sources (PostgreSQL, external APIs, etc.) can be added later
without breaking existing functionality.
"""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


class DataIngestionError(Exception):
    """Raised when a data source cannot be located or loaded correctly."""


def load_csv(file_path: str | Path) -> pd.DataFrame:
    """
    Load a CSV file into a pandas DataFrame.

    Args:
        file_path: Path to the CSV file, as a string or pathlib.Path object.
            Can be relative or absolute.

    Returns:
        pd.DataFrame: The loaded CSV data.

    Raises:
        DataIngestionError: If the file does not exist, is not a file,
            or cannot be parsed as a valid CSV.
    """
    path = Path(file_path)

    if not path.exists():
        raise DataIngestionError(f"CSV file not found: {path}")

    if not path.is_file():
        raise DataIngestionError(f"Expected a file but found a directory: {path}")

    try:
        dataframe = pd.read_csv(path)
    except pd.errors.EmptyDataError as exc:
        raise DataIngestionError(f"CSV file is empty: {path}") from exc
    except pd.errors.ParserError as exc:
        raise DataIngestionError(f"CSV file could not be parsed: {path}") from exc
    except (OSError, UnicodeDecodeError) as exc:
        raise DataIngestionError(f"CSV file could not be read: {path}") from exc

    logger.info("Loaded CSV file '%s' with shape %s", path, dataframe.shape)

    return dataframe