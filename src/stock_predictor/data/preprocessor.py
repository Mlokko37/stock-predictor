"""Data preprocessing and scaling."""
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from typing import Tuple, Optional, Union

class Preprocessor:
    def __init__(self, scaler: Optional[MinMaxScaler] = None):
        self.scaler = scaler or MinMaxScaler(feature_range=(0, 1))

    def fit_transform(self, df: pd.DataFrame, target_col: str = "Close") -> np.ndarray:
        """Fit scaler and transform target column."""
        data = df[[target_col]].values
        return self.scaler.fit_transform(data)

    def transform(self, data: Union[pd.DataFrame, np.ndarray], target_col: str = "Close") -> np.ndarray:
        """
        Transform data.
        - If DataFrame: extract target_col values.
        - If numpy array: use directly (must be 2D).
        """
        if isinstance(data, pd.DataFrame):
            return self.scaler.transform(data[[target_col]].values)
        else:
            # Assume numpy array
            if data.ndim == 1:
                data = data.reshape(-1, 1)
            return self.scaler.transform(data)

    def inverse_transform(self, scaled: np.ndarray) -> np.ndarray:
        return self.scaler.inverse_transform(scaled)

def create_sequences(data: np.ndarray, seq_length: int) -> Tuple[np.ndarray, np.ndarray]:
    """Create X,y sequences for time series forecasting."""
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length])
    return np.array(X), np.array(y)