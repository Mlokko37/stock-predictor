# src/stock_predictor/visualization/supabase_viewer.py
import streamlit as st
import pandas as pd
from ..database.supabase_db import db
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Supabase Stock Database",
    page_icon="🗄️",
    layout="wide"
)

st.title("🗄️ Stock Database Viewer")
st.markdown("View and manage stock data stored in Supabase")

# Sidebar
with st.sidebar:
    st.header("📊 Database Stats")
    
    # Get all stocks
    stocks = db.get_all_stocks()
    st.metric("Total Stocks", len(stocks))
    
    # Recent predictions
    predictions = []
    for stock in stocks[:5]:
        preds = db.get_recent_predictions(stock['symbol'], limit=1)
        predictions.extend(preds)
    st.metric("Recent Predictions", len(predictions))

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["📈 Stocks", "💰 Price Data", "🔮 Predictions", "📝 SQL Query"])

with tab1:
    st.subheader("Stock Metadata")
    if stocks:
        df_stocks = pd.DataFrame(stocks)
        
        # Filter by region
        regions = st.multiselect("Filter by Region", df_stocks['region'].unique())
        if regions:
            df_stocks = df_stocks[df_stocks['region'].isin(regions)]
        
        st.dataframe(df_stocks, use_container_width=True)
        
        # Export button
        csv = df_stocks.to_csv(index=False)
        st.download_button("📥 Export to CSV", csv, "stocks_metadata.csv", "text/csv")

with tab2:
    st.subheader("Stock Price Data")
    
    if stocks:
        selected_stock = st.selectbox("Select Stock", [f"{s['symbol']} - {s['name']}" for s in stocks])
        symbol = selected_stock.split(" - ")[0]
        
        col1, col2 = st.columns(2)
        with col1:
            days = st.number_input("Days of history", min_value=7, max_value=365, value=30)
        with col2:
            if st.button("Load Data"):
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                
                df = db.get_stock_prices(symbol, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
                
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                    
                    # Plot
                    st.subheader("Price Chart")
                    st.line_chart(df['close'])
                    
                    # Summary stats
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Start Price", f"${df['close'].iloc[0]:.2f}")
                    with col2:
                        st.metric("End Price", f"${df['close'].iloc[-1]:.2f}")
                    with col3:
                        change = ((df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0]) * 100
                        st.metric("Change", f"{change:+.2f}%")
                else:
                    st.warning("No data found")

with tab3:
    st.subheader("Recent Predictions")
    
    if stocks:
        selected_stock = st.selectbox("Select Stock for Predictions", [f"{s['symbol']} - {s['name']}" for s in stocks], key="pred_stock")
        symbol = selected_stock.split(" - ")[0]
        
        predictions = db.get_recent_predictions(symbol, limit=20)
        if predictions:
            df_pred = pd.DataFrame(predictions)
            st.dataframe(df_pred, use_container_width=True)
        else:
            st.info("No predictions found for this stock")

with tab4:
    st.subheader("Run Custom SQL Query")
    st.warning("⚠️ This requires admin privileges")
    
    query = st.text_area("SQL Query", "SELECT * FROM stocks_metadata LIMIT 10")
    if st.button("Execute"):
        try:
            # Note: This requires service role key
            result = db.client.rpc('exec_sql', {'sql': query}).execute()
            if result.data:
                df_result = pd.DataFrame(result.data)
                st.dataframe(df_result)
            else:
                st.success("Query executed successfully")
        except Exception as e:
            st.error(f"Error: {e}")
            st.info("Make sure you have added SUPABASE_SERVICE_KEY to .env file")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Powered by Supabase PostgreSQL | Real-time Stock Database</p>
</div>
""", unsafe_allow_html=True)