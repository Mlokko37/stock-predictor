# src/stock_predictor/visualization/supabase_dashboard.py
import streamlit as st
from ..database.supabase_db import db
import pandas as pd

st.title("📊 Supabase Data Viewer")
st.markdown("View stock data stored in Supabase")

# Display stocks
st.subheader("Available Stocks")
stocks = db.get_all_stocks()
if stocks:
    df_stocks = pd.DataFrame(stocks)
    st.dataframe(df_stocks)
else:
    st.info("No stocks found in database")

# Query stock prices
st.subheader("Query Stock Prices")
symbol = st.selectbox("Select Symbol", [s['symbol'] for s in stocks] if stocks else [])
if symbol:
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date")
    with col2:
        end_date = st.date_input("End Date")
    
    if st.button("Load Data"):
        df = db.get_stock_prices(symbol, str(start_date), str(end_date))
        if not df.empty:
            st.dataframe(df)
            st.line_chart(df['close'])
        else:
            st.warning("No data found")

# View predictions
st.subheader("Recent Predictions")
if symbol:
    predictions = db.get_recent_predictions(symbol)
    if predictions:
        df_pred = pd.DataFrame(predictions)
        st.dataframe(df_pred)