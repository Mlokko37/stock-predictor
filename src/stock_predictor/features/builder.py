"""Feature engineering pipeline."""
import pandas as pd
from .technical import add_sma, add_ema, add_rsi, add_macd

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add all technical indicators."""
    df = df.copy()
    df = add_sma(df, 20)
    df = add_sma(df, 50)
    df = add_ema(df, 20)
    df = add_rsi(df, 14)
    df = add_macd(df)
    # Drop rows with NaN (from rolling windows)
    df.dropna(inplace=True)
    return df