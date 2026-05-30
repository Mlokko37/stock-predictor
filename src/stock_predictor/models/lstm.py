"""LSTM model for stock price prediction."""
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import os
from pathlib import Path

class LSTMPredictor:
    """LSTM model for time series prediction."""
    
    def __init__(self, input_shape=(60, 1), units=50, dropout=0.2):
        """
        Initialize LSTM model.
        
        Args:
            input_shape: Shape of input data (sequence_length, n_features)
            units: Number of LSTM units
            dropout: Dropout rate for regularization
        """
        self.input_shape = input_shape
        self.units = units
        self.dropout = dropout
        self.model = None
        self.history = None
        
    def build_model(self):
        """Build the LSTM model architecture."""
        model = Sequential([
            LSTM(self.units, return_sequences=True, input_shape=self.input_shape),
            Dropout(self.dropout),
            LSTM(self.units, return_sequences=False),
            Dropout(self.dropout),
            Dense(25),
            Dense(1)
        ])
        
        model.compile(
            optimizer='adam',
            loss='mean_squared_error',
            metrics=['mae']
        )
        
        self.model = model
        return model
    
    def train(self, X_train, y_train, X_val, y_val, epochs=100, batch_size=32):
        """
        Train the LSTM model.
        
        Args:
            X_train: Training features
            y_train: Training targets
            X_val: Validation features
            y_val: Validation targets
            epochs: Number of training epochs
            batch_size: Batch size for training
        """
        if self.model is None:
            self.build_model()
        
        # Callbacks
        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        # Train
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stop],
            verbose=1
        )
        
        return self.history
    
    def predict(self, X, verbose=0):
        """Make predictions."""
        if self.model is None:
            raise ValueError("Model not trained or loaded")
        return self.model.predict(X, verbose=verbose)
    
    def save(self, filepath):
        """Save model to disk."""
        if self.model is None:
            raise ValueError("No model to save")
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        self.model.save(str(filepath))
        print(f"✅ Model saved to {filepath}")
    
    def load(self, filepath):
        """Load model from disk."""
        from tensorflow.keras.models import load_model
        
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        self.model = load_model(str(filepath))
        print(f"✅ Model loaded from {filepath}")
        return self.model