"""Supabase database integration for stock predictor."""
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseDB:
    """Supabase database manager for stock data."""
    
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        self.service_key = os.getenv("SUPABASE_SERVICE_KEY")
        self.initialized = False
        
        if not self.url or not self.key:
            print("⚠️ SUPABASE_URL and SUPABASE_KEY must be set in .env file")
            self.client = None
            return
        
        try:
            # Initialize Supabase client
            self.client: Client = create_client(self.url, self.key)
            self.admin_client: Optional[Client] = None
            
            if self.service_key:
                self.admin_client = create_client(self.url, self.service_key)
            
            self.initialized = True
            print("✅ Supabase client initialized")
            
            # Test connection
            self.test_connection()
            
        except Exception as e:
            print(f"❌ Failed to initialize Supabase: {e}")
            self.client = None
    
    def test_connection(self):
        """Test database connection."""
        try:
            result = self.client.table('stocks_metadata').select('count').limit(1).execute()
            print("✅ Supabase connection successful")
        except Exception as e:
            print(f"⚠️ Supabase connection test failed: {e}")
            print("   Make sure tables exist. Run SQL in Supabase SQL editor.")
    
    def save_stock_prices(self, symbol: str, df: pd.DataFrame):
        """Save stock prices to database using batch upsert."""
        if not self.initialized or not self.client:
            print(f"⚠️ Skipping save for {symbol} - Database not configured")
            return
        
        if df.empty:
            print(f"⚠️ No data to save for {symbol}")
            return
        
        records = []
        for idx, row in df.iterrows():
            records.append({
                "symbol": symbol,
                "date": idx.strftime("%Y-%m-%d") if hasattr(idx, 'strftime') else str(idx),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume'])
            })
        
        # Batch upsert (insert or update) - more efficient
        try:
            # Split into batches of 100 to avoid request size limits
            batch_size = 100
            for i in range(0, len(records), batch_size):
                batch = records[i:i+batch_size]
                self.client.table('stock_prices').upsert(batch).execute()
            print(f"✅ Saved/Updated {len(records)} records for {symbol}")
        except Exception as e:
            print(f"❌ Error saving {symbol}: {e}")
    
    def get_stock_prices(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Retrieve stock prices from database."""
        if not self.initialized or not self.client:
            return pd.DataFrame()
        
        try:
            response = self.client.table('stock_prices')\
                .select('date, open, high, low, close, volume')\
                .eq('symbol', symbol)\
                .gte('date', start_date)\
                .lte('date', end_date)\
                .order('date')\
                .execute()
            
            if response.data:
                df = pd.DataFrame(response.data)
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
                return df
            return pd.DataFrame()
        except Exception as e:
            print(f"Error retrieving data for {symbol}: {e}")
            return pd.DataFrame()
    
    def save_stock_metadata(self, symbol: str, name: str, sector: str = "", 
                           exchange: str = "", region: str = "", currency: str = "USD"):
        """Save or update stock metadata."""
        if not self.initialized or not self.client:
            return
        
        metadata = {
            "symbol": symbol,
            "name": name,
            "sector": sector,
            "exchange": exchange,
            "region": region,
            "currency": currency,
            "updated_at": datetime.now().isoformat()
        }
        
        try:
            self.client.table('stocks_metadata').upsert(metadata).execute()
            print(f"✅ Saved metadata for {symbol}")
        except Exception as e:
            print(f"❌ Error saving metadata for {symbol}: {e}")
    
    def get_all_stocks(self) -> List[Dict]:
        """Get all stocks from metadata."""
        if not self.initialized or not self.client:
            return []
        
        try:
            response = self.client.table('stocks_metadata')\
                .select('*')\
                .order('symbol')\
                .execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error fetching stocks: {e}")
            return []
    
    def get_stocks_by_region(self, region: str) -> List[Dict]:
        """Get stocks by region."""
        if not self.initialized or not self.client:
            return []
        
        try:
            response = self.client.table('stocks_metadata')\
                .select('*')\
                .eq('region', region)\
                .execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error fetching stocks by region: {e}")
            return []
    
    def save_prediction(self, symbol: str, horizon_days: int, predicted_price: float, 
                       actual_price: float = None, confidence_score: float = None):
        """Save a prediction to database."""
        if not self.initialized or not self.client:
            return
        
        record = {
            "symbol": symbol,
            "prediction_date": datetime.now().date().isoformat(),
            "horizon_days": horizon_days,
            "predicted_price": predicted_price,
            "actual_price": actual_price,
            "confidence_score": confidence_score
        }
        
        try:
            self.client.table('predictions').insert(record).execute()
            print(f"✅ Saved prediction for {symbol} ({horizon_days}d): ${predicted_price:.2f}")
        except Exception as e:
            print(f"❌ Error saving prediction for {symbol}: {e}")
    
    def get_recent_predictions(self, symbol: str, limit: int = 10) -> List[Dict]:
        """Get recent predictions for a symbol."""
        if not self.initialized or not self.client:
            return []
        
        try:
            response = self.client.table('predictions')\
                .select('*')\
                .eq('symbol', symbol)\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error fetching predictions: {e}")
            return []
    
    def delete_stock_prices(self, symbol: str):
        """Delete all price data for a symbol (useful for refresh)."""
        if not self.initialized or not self.client:
            return
        
        try:
            self.client.table('stock_prices')\
                .delete()\
                .eq('symbol', symbol)\
                .execute()
            print(f"✅ Deleted price data for {symbol}")
        except Exception as e:
            print(f"❌ Error deleting data for {symbol}: {e}")
    
    def get_database_stats(self) -> Dict:
        """Get database statistics."""
        if not self.initialized or not self.client:
            return {}
        
        try:
            stocks = len(self.get_all_stocks())
            
            # Get count of price records
            response = self.client.table('stock_prices')\
                .select('count', count='exact')\
                .execute()
            price_records = response.count if hasattr(response, 'count') else 0
            
            # Get count of predictions
            response = self.client.table('predictions')\
                .select('count', count='exact')\
                .execute()
            predictions = response.count if hasattr(response, 'count') else 0
            
            return {
                "total_stocks": stocks,
                "total_price_records": price_records,
                "total_predictions": predictions
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}

# Create global database instance
db = SupabaseDB()