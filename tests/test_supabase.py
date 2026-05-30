# test_supabase.py
from src.stock_predictor.database.supabase_db import db
from src.stock_predictor.data.collector import download_data

# Test connection
print("Testing Supabase connection...")

# Download and save data
symbol = "AAPL"
df = download_data(symbol, period="1mo")
print(f"Downloaded {len(df)} rows for {symbol}")

# Save to Supabase
db.save_stock_prices(symbol, df)
print("✅ Data saved to Supabase")

# Retrieve data
df_retrieved = db.get_stock_prices(symbol, "2024-01-01", "2025-01-01")
print(f"Retrieved {len(df_retrieved)} rows from Supabase")

# Get all stocks
stocks = db.get_all_stocks()
print(f"Total stocks in database: {len(stocks)}")