"""Sequence-to-sequence LSTM for multi-step forecasting."""
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, RepeatVector, TimeDistributed
from tensorflow.keras.callbacks import EarlyStopping

def build_seq2seq(input_shape, output_steps, lstm_units=50):
    """
    input_shape: (seq_len, n_features)
    output_steps: number of future steps to predict
    """
    model = Sequential([
        LSTM(lstm_units, input_shape=input_shape),
        RepeatVector(output_steps),
        LSTM(lstm_units, return_sequences=True),
        TimeDistributed(Dense(1))   # predict 1 feature per step (e.g., Close)
    ])
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model