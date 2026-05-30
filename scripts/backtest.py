import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parents[1]))
import pandas as pd
import numpy as np
from src.stock_predictor.models.lstm import LSTMPredictor
from src.stock_predictor.data.preprocessor import Preprocessor
import pickle

# Load model and scaler
seq_len = 60
model = LSTMPredictor(input_shape=(seq_len, 1))
model.load("models/final/lstm_model.h5")

with open("models/final/scaler.pkl", "rb") as f:
    scaler_obj = pickle.load(f)
preprocessor = Preprocessor(scaler=scaler_obj)

# Load data
df = pd.read_parquet("data/raw/AAPL.parquet")
close_prices = df["Close"].values.reshape(-1, 1)

# Scale data
scaled = preprocessor.transform(close_prices)

# Walk‑forward validation
predictions = []
actuals = []
for i in range(len(scaled) - seq_len - 1):
    X = scaled[i:i+seq_len].reshape(1, seq_len, 1)
    y_true = scaled[i+seq_len]
    y_pred = model.predict(X, verbose=0)   # now works
    predictions.append(y_pred[0, 0])
    actuals.append(y_true[0])

# Inverse transform
pred_prices = preprocessor.inverse_transform(np.array(predictions).reshape(-1, 1))
true_prices = preprocessor.inverse_transform(np.array(actuals).reshape(-1, 1))

# Metrics (now safe to print without indexing)
rmse = np.sqrt(np.mean((true_prices - pred_prices)**2))
mape = np.mean(np.abs((true_prices - pred_prices) / true_prices)) * 100

print(f"RMSE: {rmse:.2f}")
print(f"MAPE: {mape:.2f}%")