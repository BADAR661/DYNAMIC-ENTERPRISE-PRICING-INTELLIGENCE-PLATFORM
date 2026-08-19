"""
Data cleaning utilities for the Enterprise Dynamic Pricing Intelligence Platform.

This module provides reusable functions for cleaning and preparing datasets
before feature engineering and downstream analytics.
"""

import pandas as pd


def clean_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Perform basic cleaning operations on a pandas DataFrame.

    Cleaning operations:
        1. Remove duplicate rows.
        2. Strip leading and trailing whitespace from column names.
        3. Return a cleaned copy of the DataFrame.

    Args:
        dataframe: The pandas DataFrame to clean.

    Returns:
        pd.DataFrame: A cleaned copy of the input DataFrame.
    """

    cleaned_dataframe = dataframe.copy()

    # Remove duplicate rows.
    cleaned_dataframe = cleaned_dataframe.drop_duplicates()

    # Remove unnecessary whitespace from column names.
    cleaned_dataframe.columns = cleaned_dataframe.columns.str.strip()

    return cleaned_dataframe