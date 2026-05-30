# src/stock_predictor/visualization/streamlit_dashboard.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go  # type: ignore[import]
import plotly.express as px  # type: ignore[import]
import requests
from datetime import datetime, timedelta
from typing import Dict, List
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Global Stock Predictor",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        background-color: #007bff;
        color: white;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #0056b3;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🌍 Global Stock Price Predictor")
st.markdown("### LSTM Neural Network - Multi-Market Predictions")
st.markdown("---")

# API endpoint
API_URL = "http://127.0.0.1:8000"

# Sidebar
with st.sidebar:
    st.header("🎮 Controls")
    
    # Market selection
    st.subheader("📍 Market Selection")
    market = st.selectbox(
        "Select Market",
        ["All Markets", "🇺🇸 US Markets", "🇰🇪 Kenya NSE", "🇳🇬 Nigeria NGX", "🇿🇦 South Africa JSE", "🌍 African Markets", "🛢️ Oil & Gas", "🏦 Banking Sector"]
    )
    
    # Stock selection based on market
    stocks_by_market: dict[str, list[dict[str, str]]] = {
        "🇺🇸 US Markets": [
            {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology"},
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology"},
            {"symbol": "MSFT", "name": "Microsoft", "sector": "Technology"},
            {"symbol": "TSLA", "name": "Tesla Inc.", "sector": "Automotive"},
            {"symbol": "AMZN", "name": "Amazon", "sector": "E-commerce"},
            {"symbol": "META", "name": "Meta Platforms", "sector": "Technology"},
            {"symbol": "XOM", "name": "Exxon Mobil", "sector": "Oil & Gas"},
            {"symbol": "CVX", "name": "Chevron", "sector": "Oil & Gas"},
        ],
        "🇰🇪 Kenya NSE": [
            {"symbol": "SCOM.NR", "name": "Safaricom", "sector": "Telecommunications"},
            {"symbol": "KPLC.NR", "name": "Kenya Power", "sector": "Energy"},
            {"symbol": "EQTY.NR", "name": "Equity Bank", "sector": "Banking"},
            {"symbol": "KCB.NR", "name": "KCB Group", "sector": "Banking"},
            {"symbol": "COOP.NR", "name": "Co-op Bank", "sector": "Banking"},
            {"symbol": "EABL.NR", "name": "East African Breweries", "sector": "Beverages"},
            {"symbol": "TOTL.NR", "name": "TotalEnergies Kenya", "sector": "Oil & Gas"},
            {"symbol": "KEGN.NR", "name": "Kenya Electricity Generating", "sector": "Energy"},
        ],
        "🇳🇬 Nigeria NGX": [
            {"symbol": "MTNN.LG", "name": "MTN Nigeria", "sector": "Telecommunications"},
            {"symbol": "GUARANTY.LG", "name": "Guaranty Trust Bank", "sector": "Banking"},
            {"symbol": "ZENITHBANK.LG", "name": "Zenith Bank", "sector": "Banking"},
            {"symbol": "DANGSUGAR.LG", "name": "Dangote Sugar", "sector": "Food"},
        ],
        "🇿🇦 South Africa JSE": [
            {"symbol": "NPS.JO", "name": "Naspers", "sector": "Technology"},
            {"symbol": "FSR.JO", "name": "FirstRand", "sector": "Banking"},
            {"symbol": "SBK.JO", "name": "Standard Bank", "sector": "Banking"},
            {"symbol": "AGL.JO", "name": "Anglo American", "sector": "Mining"},
            {"symbol": "SOL.JO", "name": "Sasol", "sector": "Oil & Gas"},
        ],
        "🌍 African Markets": [
            {"symbol": "SCOM.NR", "name": "Safaricom (Kenya)", "sector": "Telecom"},
            {"symbol": "MTNN.LG", "name": "MTN Nigeria", "sector": "Telecom"},
            {"symbol": "NPS.JO", "name": "Naspers (SA)", "sector": "Tech"},
            {"symbol": "FSR.JO", "name": "FirstRand (SA)", "sector": "Banking"},
        ],
        "🛢️ Oil & Gas": [
            {"symbol": "XOM", "name": "Exxon Mobil", "region": "US"},
            {"symbol": "CVX", "name": "Chevron", "region": "US"},
            {"symbol": "TOTL.NR", "name": "TotalEnergies Kenya", "region": "Kenya"},
            {"symbol": "SOL.JO", "name": "Sasol", "region": "SA"},
        ],
        "🏦 Banking Sector": [
            {"symbol": "JPM", "name": "JPMorgan Chase", "region": "US"},
            {"symbol": "EQTY.NR", "name": "Equity Bank", "region": "Kenya"},
            {"symbol": "KCB.NR", "name": "KCB Group", "region": "Kenya"},
            {"symbol": "GUARANTY.LG", "name": "GT Bank", "region": "Nigeria"},
            {"symbol": "FSR.JO", "name": "FirstRand", "region": "SA"},
        ]
    }
    
    # Get stock list based on market selection
    stock_list: list[dict[str, str]] = []
    if market == "All Markets":
        stock_list = [stock for market_stocks in stocks_by_market.values() for stock in market_stocks]
    else:
        stock_list = stocks_by_market.get(market, [])
    
    # Create selectbox for stocks
    stock_options = {f"{s['name']} ({s['symbol']})": s['symbol'] for s in stock_list}
    selected_stock_label = st.selectbox("Select Stock", list(stock_options.keys()))
    selected_symbol = stock_options[selected_stock_label]
    selected_stock_info = next((s for s in stock_list if s['symbol'] == selected_symbol), {})
    
    st.divider()
    
    # Date range
    st.subheader("📅 Date Range")
    col1, col2 = st.columns(2)
    with col1:
        end_date = st.date_input("End Date", datetime.now())
    with col2:
        start_date = st.date_input("Start Date", end_date - timedelta(days=365))
    
    st.divider()
    
    # Prediction settings
    st.subheader("🔮 Prediction Settings")
    horizons = st.multiselect(
        "Prediction Horizons (days)",
        options=[1, 5, 10, 20, 30],
        default=[1, 5, 10]
    )
    
    st.divider()
    
    # API Status
    st.subheader("🔌 API Status")
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            st.success("✅ API Connected")
        else:
            st.error("❌ API Error")
    except:
        st.error("❌ API Not Connected")
        st.info("Run: uvicorn src.stock_predictor.api.main:app --reload")

# Main content area
if selected_symbol:
    # Stock header
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.header(f"{selected_stock_info.get('name', selected_symbol)}")
        st.caption(f"Symbol: {selected_symbol} | Sector: {selected_stock_info.get('sector', 'N/A')}")
    
    # Main prediction button
    if st.button("🚀 Generate Predictions", type="primary", use_container_width=True):
        
        # Fetch historical data
        with st.spinner("Fetching historical data..."):
            params = {
                "symbol": selected_symbol,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d")
            }
            
            try:
                hist_response = requests.get(f"{API_URL}/predict/historical", params=params)
                
                if hist_response.status_code == 200:
                    hist_data = hist_response.json()
                    
                    # Create DataFrame
                    df_historical = pd.DataFrame({
                        'date': pd.to_datetime(hist_data['dates']),
                        'price': hist_data['prices']
                    })
                    
                    # Get predictions if horizons selected
                    if horizons:
                        with st.spinner("Computing predictions..."):
                            predict_payload = {
                                "symbol": selected_symbol,
                                "start_date": start_date.strftime("%Y-%m-%d"),
                                "end_date": end_date.strftime("%Y-%m-%d"),
                                "horizons": horizons
                            }
                            
                            pred_response = requests.post(
                                f"{API_URL}/predict/with_history",
                                json=predict_payload
                            )
                            
                            if pred_response.status_code == 200:
                                pred_data = pred_response.json()
                                
                                # Create Plotly figure
                                fig = go.Figure()
                                
                                # Add historical price line
                                fig.add_trace(go.Scatter(
                                    x=df_historical['date'],
                                    y=df_historical['price'],
                                    mode='lines',
                                    name='Historical Price',
                                    line=dict(color='#1f77b4', width=2),
                                    fill='tozeroy',
                                    fillcolor='rgba(31, 119, 180, 0.1)'
                                ))
                                
                                # Get last price
                                last_date = df_historical['date'].iloc[-1]
                                last_price = df_historical['price'].iloc[-1]
                                
                                # Add predictions
                                colors = ['#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
                                for idx, (horizon, price) in enumerate(pred_data['predictions'].items()):
                                    days = int(horizon.replace('d', ''))
                                    future_date = last_date + timedelta(days=days)
                                    
                                    # Add prediction point
                                    fig.add_trace(go.Scatter(
                                        x=[future_date],
                                        y=[price],
                                        mode='markers+text',
                                        name=f'{horizon} Prediction',
                                        marker=dict(
                                            size=15,
                                            symbol='star',
                                            color=colors[idx % len(colors)],
                                            line=dict(width=2, color='white')
                                        ),
                                        text=[f'${price:.2f}'],
                                        textposition='top center',
                                        textfont=dict(size=10, color='black')
                                    ))
                                    
                                    # Add connecting line
                                    fig.add_trace(go.Scatter(
                                        x=[last_date, future_date],
                                        y=[last_price, price],
                                        mode='lines',
                                        line=dict(dash='dash', width=1, color='gray'),
                                        showlegend=False,
                                        hoverinfo='none'
                                    ))
                                
                                # Update layout
                                fig.update_layout(
                                    title=f"{selected_stock_info.get('name', selected_symbol)} - Price Forecast",
                                    xaxis_title="Date",
                                    yaxis_title="Price (USD)",
                                    hovermode='x unified',
                                    template='plotly_white',
                                    height=500,
                                    showlegend=True,
                                    legend=dict(
                                        yanchor="top",
                                        y=0.99,
                                        xanchor="left",
                                        x=0.01,
                                        bgcolor='rgba(255, 255, 255, 0.8)'
                                    )
                                )
                                
                                # Add range slider
                                fig.update_xaxes(rangeslider_visible=True)
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Display predictions in metrics
                                st.subheader("📊 Price Predictions")
                                
                                # Create metrics row
                                cols = st.columns(len(pred_data['predictions']))
                                for idx, (horizon, price) in enumerate(pred_data['predictions'].items()):
                                    with cols[idx]:
                                        change = ((price - last_price) / last_price) * 100
                                        st.metric(
                                            label=f"{horizon} Forecast",
                                            value=f"${price:.2f}",
                                            delta=f"{change:+.2f}%"
                                        )
                                
                                # Recent data table
                                with st.expander("📋 View Recent Historical Data"):
                                    recent_df = df_historical.tail(10).sort_values('date', ascending=False)
                                    recent_df['date'] = recent_df['date'].dt.strftime('%Y-%m-%d')
                                    recent_df = recent_df.rename(columns={'date': 'Date', 'price': 'Close Price'})
                                    recent_df['Close Price'] = recent_df['Close Price'].apply(lambda x: f"${x:.2f}")
                                    st.dataframe(recent_df, use_container_width=True, hide_index=True)
                                
                                # Download buttons
                                col1, col2 = st.columns(2)
                                with col1:
                                    predictions_df = pd.DataFrame([
                                        {"Horizon": k, "Predicted Price": f"${v:.2f}", "Change %": f"{((v - last_price) / last_price) * 100:+.2f}%"}
                                        for k, v in pred_data['predictions'].items()
                                    ])
                                    csv_pred = predictions_df.to_csv(index=False)
                                    st.download_button(
                                        label="📥 Download Predictions (CSV)",
                                        data=csv_pred,
                                        file_name=f"{selected_symbol}_predictions.csv",
                                        mime="text/csv"
                                    )
                                
                                with col2:
                                    csv_hist = df_historical.to_csv(index=False)
                                    st.download_button(
                                        label="📥 Download Historical Data (CSV)",
                                        data=csv_hist,
                                        file_name=f"{selected_symbol}_historical.csv",
                                        mime="text/csv"
                                    )
                                
                            else:
                                st.error(f"Prediction API Error: {pred_response.status_code}")
                                if pred_response.text:
                                    st.json(pred_response.json())
                    else:
                        st.warning("Please select at least one prediction horizon")
                else:
                    st.error(f"Historical data API Error: {hist_response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Make sure the FastAPI server is running at http://127.0.0.1:8000")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p>🌍 Global Stock Predictor - Powered by LSTM Neural Network</p>
    <p>Supported Markets: 🇺🇸 US | 🇰🇪 Kenya | 🇳🇬 Nigeria | 🇿🇦 South Africa | 🌍 Africa</p>
    <p><small>Predictions are for educational purposes only. Not financial advice.</small></p>
</div>
""", unsafe_allow_html=True)