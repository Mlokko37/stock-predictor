"""Backtesting logic."""
import pandas as pd
import numpy as np
from ..models.baseline import NaivePredictor

class BacktestEngine:
    def __init__(self, data: pd.DataFrame, model, preprocessor, seq_length: int):
        self.data = data
        self.model = model
        self.preprocessor = preprocessor
        self.seq_length = seq_length

    def run(self, start_idx: int = 0):
        predictions = []
        actuals = []
        for i in range(start_idx + self.seq_length, len(self.data)):
            hist = self.data.iloc[i - self.seq_length:i]["Close"].values.reshape(-1, 1)
            hist_scaled = self.preprocessor.transform(hist)
            pred_scaled = self.model.predict(hist_scaled.reshape(1, self.seq_length, 1))
            pred = self.preprocessor.inverse_transform(pred_scaled)[0, 0]
            actual = self.data.iloc[i]["Close"]
            predictions.append(pred)
            actuals.append(actual)
        return pd.DataFrame({"predicted": predictions, "actual": actuals})