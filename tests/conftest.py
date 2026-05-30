import pytest
from stock_predictor.data.collector import DataCollector

@pytest.fixture
def sample_data():
    return {"AAPL": [150, 152, 151]}