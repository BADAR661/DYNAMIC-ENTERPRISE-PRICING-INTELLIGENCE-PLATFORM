"""
Data validation utilities for the Enterprise Dynamic Pricing Intelligence Platform.

This module provides reusable functions for checking raw and processed
datasets before they move further into the data pipeline.
"""

import pandas as pd


def validate_dataframe(dataframe: pd.DataFrame) -> dict:
    """
    Validate a pandas DataFrame for common data quality issues.

    Args:
        dataframe: The pandas DataFrame to validate.

    Returns:
        dict: A validation report containing:
            - row_count
            - column_count
            - missing_values
            - duplicate_rows
            - data_types
    """

    validation_report = {
        "row_count": len(dataframe),
        "column_count": len(dataframe.columns),
        "missing_values": dataframe.isnull().sum().to_dict(),
        "duplicate_rows": int(dataframe.duplicated().sum()),
        "data_types": dataframe.dtypes.astype(str).to_dict(),
    }

    return validation_report