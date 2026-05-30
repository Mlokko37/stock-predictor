"""Technical indicators."""
import pandas as pd
import numpy as np

def add_sma(df: pd.DataFrame, window: int = 20, column: str = "Close") -> pd.DataFrame:
    df[f"SMA_{window}"] = df[column].rolling(window=window).mean()
    return df

def add_ema(df: pd.DataFrame, span: int = 20, column: str = "Close") -> pd.DataFrame:
    df[f"EMA_{span}"] = df[column].ewm(span=span, adjust=False).mean()
    return df

def add_rsi(df: pd.DataFrame, window: int = 14, column: str = "Close") -> pd.DataFrame:
    delta = df[column].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))
    return df

def add_macd(df: pd.DataFrame) -> pd.DataFrame:
    exp1 = df["Close"].ewm(span=12, adjust=False).mean()
    exp2 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = exp1 - exp2
    df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    return df