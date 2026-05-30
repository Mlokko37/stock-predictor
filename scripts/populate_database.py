# scripts/populate_database.py
"""Populate Supabase database with stock data."""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.stock_predictor.data.collector import download_data
from src.stock_predictor.database.supabase_db import db
import time

# List of stocks to populate
STOCKS = [
    # US Stocks
    ("AAPL", "Apple Inc.", "Technology", "NASDAQ", "US", "USD"),
    ("GOOGL", "Alphabet Inc.", "Technology", "NASDAQ", "US", "USD"),
    ("MSFT", "Microsoft", "Technology", "NASDAQ", "US", "USD"),
    ("TSLA", "Tesla Inc.", "Automotive", "NASDAQ", "US", "USD"),
    ("XOM", "Exxon Mobil", "Oil & Gas", "NYSE", "US", "USD"),
    ("CVX", "Chevron", "Oil & Gas", "NYSE", "US", "USD"),
    
    # Kenyan Stocks (NSE)
    ("SCOM.NR", "Safaricom", "Telecommunications", "NSE", "Kenya", "KES"),
    ("KPLC.NR", "Kenya Power", "Energy", "NSE", "Kenya", "KES"),
    ("EQTY.NR", "Equity Bank", "Banking", "NSE", "Kenya", "KES"),
    ("KCB.NR", "KCB Group", "Banking", "NSE", "Kenya", "KES"),
    ("EABL.NR", "East African Breweries", "Beverages", "NSE", "Kenya", "KES"),
    ("TOTL.NR", "TotalEnergies Kenya", "Oil & Gas", "NSE", "Kenya", "KES"),
    
    # Nigerian Stocks
    ("MTNN.LG", "MTN Nigeria", "Telecommunications", "NGX", "Nigeria", "NGN"),
    
    # South African Stocks
    ("NPS.JO", "Naspers", "Technology", "JSE", "South Africa", "ZAR"),
]

def populate_database():
    """Populate database with stock data."""
    print("🌍 Starting database population...")
    print("=" * 50)
    
    for symbol, name, sector, exchange, region, currency in STOCKS:
        print(f"\n📊 Processing {symbol} - {name}")
        
        # Save metadata
        metadata = {
            "name": name,
            "sector": sector,
            "exchange": exchange,
            "region": region,
            "currency": currency
        }
        db.save_stock_metadata(symbol, metadata)
        
        # Download and save price data
        try:
            print(f"  Downloading data for {symbol}...")
            df = download_data(symbol, period="2y", interval="1d")
            
            if not df.empty:
                db.save_stock_prices(symbol, df)
                print(f"  ✅ Saved {len(df)} price records")
            else:
                print(f"  ⚠️ No data found for {symbol}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        # Rate limiting to avoid API throttling
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print("✅ Database population complete!")
    
    # Show summary
    stocks = db.get_all_stocks()
    print(f"\n📈 Total stocks in database: {len(stocks)}")
    for stock in stocks[:10]:  # Show first 10
        print(f"  - {stock['symbol']}: {stock['name']} ({stock['region']})")

if __name__ == "__main__":
    populate_database()