"""Prediction endpoint using saved scaler with global stock support."""
from fastapi import APIRouter, HTTPException
from ..schemas import PredictionRequest, PredictionResponse
from ...models.lstm import LSTMPredictor
from ...data.collector import global_collector, download_data
from ...data.preprocessor import Preprocessor
import numpy as np
import pickle
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel

# Try to import db, but don't fail if not available
try:
    from ...database.supabase_db import db
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    class DummyDB:
        def get_all_stocks(self): return []
        def get_database_stats(self): return {}
    db = DummyDB()

class PredictionRequestWithHorizons(BaseModel):
    symbol: str
    start_date: str
    end_date: str
    horizons: List[int]

router = APIRouter(prefix="/predict", tags=["prediction"])

MODEL_PATH = Path("models/final/lstm_model.h5")
SCALER_PATH = Path("models/final/scaler.pkl")
SEQ_LENGTH = 60

_model = None
_scaler = None

def load_model_and_scaler():
    global _model, _scaler
    if _model is None and MODEL_PATH.exists():
        _model = LSTMPredictor(input_shape=(SEQ_LENGTH, 1))
        _model.load(str(MODEL_PATH))
    if _scaler is None and SCALER_PATH.exists():
        with open(SCALER_PATH, "rb") as f:
            scaler_obj = pickle.load(f)
        _scaler = Preprocessor(scaler=scaler_obj)
    return _model, _scaler

@router.get("/symbols")
async def get_symbols():
    """Return list of available stock symbols including global and NSE stocks."""
    all_symbols = global_collector.get_all_symbols()
    
    # Format symbols for dropdown
    symbols_list = []
    for symbol, info in all_symbols.items():
        symbols_list.append({
            "value": symbol,
            "label": f"{info['name']} ({symbol}) - {info['region']}"
        })
    
    # Add NSE specific label
    nse_stocks = global_collector.get_nse_stocks()
    for stock in nse_stocks:
        symbols_list.append({
            "value": stock['symbol'],
            "label": f"🇰🇪 {stock['name']} ({stock['symbol']}) - NSE"
        })
    
    return {"symbols": symbols_list}

@router.get("/global/symbols")
async def get_global_symbols(region: Optional[str] = None):
    """Get global stock symbols filtered by region."""
    if region:
        symbols = global_collector.GLOBAL_STOCKS.get(region, {})
    else:
        symbols = global_collector.get_all_symbols()
    
    return {"symbols": symbols, "total": len(symbols)}

@router.get("/nse/stocks")
async def get_nse_stocks():
    """Get all Nairobi Securities Exchange stocks."""
    return {"stocks": global_collector.get_nse_stocks()}

@router.get("/historical")
async def get_historical(symbol: str, start_date: str, end_date: str):
    """Return historical closing prices for Chart.js."""
    try:
        import pandas as pd
        
        df = download_data(symbol, period="2y", interval="1d")
        
        # Ensure index is datetime
        df.index = pd.to_datetime(df.index)
        
        # Filter by date range
        mask = (df.index >= start_date) & (df.index <= end_date)
        df_filtered = df.loc[mask]
        
        if df_filtered.empty:
            raise HTTPException(404, f"No data found for {symbol} in date range")
        
        # Convert dates to string format safely
        dates = [d.strftime("%Y-%m-%d") for d in df_filtered.index]
        prices = df_filtered["Close"].tolist()
        
        return {"dates": dates, "prices": prices}
    except Exception as e:
        print(f"Error in get_historical: {e}")
        raise HTTPException(500, f"Error fetching historical data: {str(e)}")

@router.post("/", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Predict for any global stock."""
    model, scaler = load_model_and_scaler()
    if model is None:
        raise HTTPException(503, "Model not trained yet. Run training first.")
    if scaler is None:
        raise HTTPException(503, "Scaler not found. Re-run training to save scaler.")

    df = download_data(request.symbol, period="3mo", interval="1d")
    if len(df) < SEQ_LENGTH + 1:
        raise HTTPException(400, f"Not enough data for {request.symbol}. Need at least {SEQ_LENGTH+1} days.")
    
    last_sequence = df["Close"].values[-SEQ_LENGTH:].reshape(-1, 1)
    last_sequence_scaled = scaler.transform(last_sequence)
    pred_scaled = model.predict(last_sequence_scaled.reshape(1, SEQ_LENGTH, 1), verbose=0)
    pred_price = scaler.inverse_transform(pred_scaled)[0, 0]
    
    # Get stock info
    all_symbols = global_collector.get_all_symbols()
    stock_info = all_symbols.get(request.symbol, {})
    
    return PredictionResponse(
        symbol=request.symbol,
        predicted_price=float(pred_price),
        last_actual_price=float(df["Close"].iloc[-1])
    )

@router.get("/db/stats")
async def get_db_stats():
    """Get database statistics."""
    stocks = db.get_all_stocks()
    return {
        "total_stocks": len(stocks),
        "stocks_by_region": {}
    }

@router.get("/db/stocks")
async def get_db_stocks():
    """Get all stocks from database."""
    return {"stocks": db.get_all_stocks()}    

@router.post("/with_history")
async def predict_with_history(req: PredictionRequestWithHorizons):
    """Return historical data + multi-step predictions for chosen horizons."""
    model, scaler = load_model_and_scaler()
    if model is None or scaler is None:
        raise HTTPException(503, "Model not ready")

    # Get full data for the last sequence
    full_df = download_data(req.symbol, period="2y", interval="1d")
    if len(full_df) < SEQ_LENGTH:
        raise HTTPException(400, f"Not enough data for {req.symbol}. Need at least {SEQ_LENGTH} days.")

    # Historical data for the chart
    hist_df = full_df.loc[req.start_date:req.end_date]
    if hist_df.empty:
        raise HTTPException(404, "No historical data for the selected date range.")
    historical = {
        "dates": hist_df.index.strftime("%Y-%m-%d").tolist(),
        "prices": hist_df["Close"].tolist()
    }

    # Last SEQ_LENGTH values
    last_sequence = full_df["Close"].values[-SEQ_LENGTH:].reshape(-1, 1)
    scaled_seq = scaler.transform(last_sequence)

    max_horizon = max(req.horizons)
    predictions = {}
    seq = scaled_seq.copy()
    for day in range(1, max_horizon + 1):
        pred_scaled = model.predict(seq.reshape(1, SEQ_LENGTH, 1), verbose=0)
        seq = np.append(seq[1:], pred_scaled, axis=0)
        if day in req.horizons:
            price = scaler.inverse_transform(pred_scaled)[0, 0]
            predictions[f"{day}d"] = float(price)

    return {"historical": historical, "predictions": predictions}