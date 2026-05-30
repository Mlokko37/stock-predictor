"""Baseline models: naive forecast (last value) and moving average."""
import numpy as np

class NaivePredictor:
    def predict(self, last_value: float) -> float:
        return last_value

class MovingAveragePredictor:
    def __init__(self, window: int = 5):
        self.window = window
        self.history = []

    def update(self, value: float):
        self.history.append(value)
        if len(self.history) > self.window:
            self.history.pop(0)

    def predict(self) -> float:
        return np.mean(self.history) if self.history else 0.0