"""Plot predictions vs actuals."""
import matplotlib.pyplot as plt
import pandas as pd

def plot_predictions(actual: pd.Series, predicted: pd.Series, title: str = "Stock Price Prediction"):
    plt.figure(figsize=(12, 6))
    plt.plot(actual.index, actual, label="Actual", color="blue")
    plt.plot(actual.index, predicted, label="Predicted", color="red", linestyle="--")
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    return plt