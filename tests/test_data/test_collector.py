import pytest
from src.stock_predictor.data.collector import download_data

def test_download_data():
    df = download_data("AAPL", period="5d", interval="1d")
    assert not df.empty
    assert "Close" in df.columns