"""Download historical data for multiple stocks globally."""
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.stock_predictor.data.collector import global_collector

def main():
    # Download data for various markets
    stocks_to_download = [
        # US Stocks
        "AAPL", "GOOGL", "MSFT", "TSLA", "XOM", "CVX",
        # Kenyan Stocks (NSE)
        "SCOM.NR", "KPLC.NR", "EQTY.NR", "KCB.NR", "EABL.NR", "TOTL.NR",
        # Nigerian Stocks
        "MTNN.LG", "GUARANTY.LG",
        # South African Stocks
        "NPS.JO", "FSR.JO"
    ]
    
    data_dir = Path("data/raw")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    for symbol in stocks_to_download:
        print(f"Downloading {symbol}...")
        try:
            df = global_collector.download_data(
                symbol, 
                period="2y", 
                save_path=data_dir / f"{symbol}.parquet"
            )
            print(f"✅ Saved {len(df)} rows for {symbol}")
        except Exception as e:
            print(f"❌ Failed to download {symbol}: {e}")

if __name__ == "__main__":
    main()