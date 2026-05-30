# test_db.py
from src.stock_predictor.database.supabase_db import db

print("Testing Supabase Database...")
print("=" * 50)

# Test connection
if db.initialized:
    print("✅ Database initialized")
    
    # Get all stocks
    stocks = db.get_all_stocks()
    print(f"\n📊 Stocks in database: {len(stocks)}")
    for stock in stocks[:5]:
        print(f"   - {stock['symbol']}: {stock['name']} ({stock['region']})")
    
    # Get stats
    stats = db.get_database_stats()
    print(f"\n📈 Database Stats:")
    print(f"   Total stocks: {stats.get('total_stocks', 0)}")
    print(f"   Price records: {stats.get('total_price_records', 0)}")
    print(f"   Predictions: {stats.get('total_predictions', 0)}")
else:
    print("❌ Database not initialized. Check your .env file.")