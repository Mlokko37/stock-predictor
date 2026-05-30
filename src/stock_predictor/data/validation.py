"""Validate data integrity."""
import pandas as pd

def validate_data(df: pd.DataFrame) -> bool:
    """Check for missing values, duplicates, and correct columns."""
    required_cols = {"Open", "High", "Low", "Close", "Volume"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Missing columns. Required: {required_cols}")
    if df.isnull().sum().sum() > 0:
        raise ValueError("Missing values detected.")
    if df.index.duplicated().any():
        raise ValueError("Duplicate timestamps.")
    return True