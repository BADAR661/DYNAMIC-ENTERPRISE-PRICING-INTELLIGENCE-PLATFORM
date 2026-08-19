"""
Data transformation utilities for the Enterprise Dynamic Pricing Intelligence Platform.

This module provides reusable functions for converting raw data columns
into appropriate data types for analytics and feature engineering.
"""

import pandas as pd


def convert_date_column(
    dataframe: pd.DataFrame,
    column_name: str,
) -> pd.DataFrame:
    """
    Convert a DataFrame column to pandas datetime format.

    Args:
        dataframe: The pandas DataFrame to transform.
        column_name: The name of the column containing date values.

    Returns:
        pd.DataFrame: A transformed copy of the DataFrame.

    Raises:
        KeyError: If the specified column does not exist.
    """

    transformed_dataframe = dataframe.copy()

    if column_name not in transformed_dataframe.columns:
        raise KeyError(
            f"Column '{column_name}' does not exist in the DataFrame."
        )

    transformed_dataframe[column_name] = pd.to_datetime(
        transformed_dataframe[column_name],
        errors="coerce",
    )

    return transformed_dataframe