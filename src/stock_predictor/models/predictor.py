"""Prediction interface."""
import numpy as np

class Predictor:
    def __init__(self, model, preprocessor, seq_length):
        self.model = model
        self.preprocessor = preprocessor
        self.seq_length = seq_length

    def predict_next(self, last_sequence: np.ndarray) -> float:
        """Predict next value given last sequence (scaled)."""
        pred_scaled = self.model.predict(last_sequence.reshape(1, self.seq_length, 1))
        return self.preprocessor.inverse_transform(pred_scaled)[0, 0]