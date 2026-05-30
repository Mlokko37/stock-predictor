"""Full training script with feature engineering, multi‑feature scaling, and seq2seq LSTM."""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parents[3]))
import pandas as pd
import pickle
import numpy as np
from src.stock_predictor.data.preprocessor import Preprocessor
from src.stock_predictor.features.builder import build_features
from src.stock_predictor.models.seq2seq import build_seq2seq
from src.stock_predictor.utils.config import load_config
from src.stock_predictor.utils.logging import setup_logger

logger = setup_logger(__name__)

def create_multi_step_sequences(data, seq_length, output_steps):
    """Create input sequences and multi‑step targets."""
    X, y = [], []
    for i in range(len(data) - seq_length - output_steps + 1):
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length:i+seq_length+output_steps, 0])  # predict only the first feature (Close)
    return np.array(X), np.array(y)

def main():
    config = load_config("default.yaml")
    data_dir = Path("data/raw")
    symbol = "AAPL"   # change to any symbol available in data/raw/
    
    # Load raw data
    df = pd.read_parquet(data_dir / f"{symbol}.parquet")
    
    # Add technical indicators
    df = build_features(df)
    
    # Choose features
    feature_cols = ["Close", "SMA_20", "RSI", "MACD"]
    df_features = df[feature_cols].copy()
    df_features.dropna(inplace=True)
    
    # Scale all features
    preprocessor = Preprocessor()
    scaled_data = preprocessor.fit_transform(df_features)   # shape (n_samples, n_features)
    
    seq_len = config["model"].get("seq_length", 60)
    output_steps = config["model"].get("output_steps", 10)   # predict 10 days ahead
    n_features = scaled_data.shape[1]
    
    # Create multi‑step sequences
    X, y = create_multi_step_sequences(scaled_data, seq_len, output_steps)
    # y shape: (samples, output_steps)
    y = y.reshape((y.shape[0], y.shape[1], 1))   # (samples, output_steps, 1)
    
    # Train/validation split
    split = int(0.8 * len(X))
    X_train, X_val = X[:split], X[split:]
    y_train, y_val = y[:split], y[split:]
    
    # Build seq2seq model
    model = build_seq2seq(input_shape=(seq_len, n_features), output_steps=output_steps)
    
    # Train
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=config["model"].get("epochs", 100),
        batch_size=config["model"].get("batch_size", 32),
        verbose=1,
        callbacks=[tf.keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True)]
    )
    
    # Save model, scaler, and feature columns
    model_dir = Path("models/final")
    model_dir.mkdir(parents=True, exist_ok=True)
    model.save(str(model_dir / "seq2seq_model.h5"))
    with open(model_dir / "scaler.pkl", "wb") as f:
        pickle.dump(preprocessor.scaler, f)
    with open(model_dir / "feature_cols.pkl", "wb") as f:
        pickle.dump(feature_cols, f)
    
    logger.info(f"Seq2Seq model, scaler, and feature_cols saved to {model_dir}")

if __name__ == "__main__":
    # Required import inside main guard to avoid circular issues
    import tensorflow as tf
    main()