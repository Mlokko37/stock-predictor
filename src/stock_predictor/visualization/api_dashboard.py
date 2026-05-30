# src/stock_predictor/visualization/api_dashboard.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
import json

# API configuration
API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Stock Predictor Dashboard (API)",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Stock Price Predictor - API Dashboard")
st.markdown("Connected to FastAPI backend")

# Sidebar for configuration
st.sidebar.header("Configuration")

# Test API connection
try:
    response = requests.get(f"{API_BASE_URL}/")
    if response.status_code == 200:
        st.sidebar.success("✅ Connected to API")
        api_info = response.json()
        st.sidebar.info(f"API: {api_info.get('name', 'Stock Predictor API')}")
    else:
        st.sidebar.error("❌ API connection failed")
except:
    st.sidebar.error("❌ Cannot connect to API. Make sure the server is running.")

# Stock selection
st.sidebar.header("Stock Selection")
stock_symbol = st.sidebar.selectbox(
    "Select Stock",
    ["AAPL", "GOOGL", "MSFT", "TSLA"],
    help="Choose a stock to predict"
)

# Prediction days
prediction_days = st.sidebar.slider(
    "Prediction Days",
    min_value=1,
    max_value=30,
    value=7,
    help="Number of days to predict ahead"
)

# Model parameters (if API supports them)
st.sidebar.header("Model Settings")
sequence_length = st.sidebar.number_input(
    "Sequence Length",
    min_value=10,
    max_value=100,
    value=60,
    help="Number of previous days to use for prediction"
)

# Main content area
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Make Prediction")
    
    if st.button(f"Predict {stock_symbol} for next {prediction_days} days", type="primary"):
        with st.spinner("Getting predictions from API..."):
            try:
                # Call prediction API
                response = requests.post(
                    f"{API_BASE_URL}/predict",
                    json={
                        "symbol": stock_symbol,
                        "days": prediction_days,
                        "sequence_length": sequence_length
                    }
                )
                
                if response.status_code == 200:
                    prediction_data = response.json()
                    
                    # Display predictions
                    st.success("Prediction successful!")
                    
                    # Create dataframe for predictions
                    pred_df = pd.DataFrame(prediction_data['predictions'])
                    pred_df['date'] = pd.to_datetime(pred_df['date'])
                    
                    # Show prediction metrics
                    st.metric(
                        "Expected Price in {} days".format(prediction_days),
                        f"${pred_df['predicted_price'].iloc[-1]:.2f}",
                        delta=f"{((pred_df['predicted_price'].iloc[-1] / pred_df['predicted_price'].iloc[0]) - 1) * 100:.2f}%"
                    )
                    
                    # Display the dataframe
                    st.dataframe(pred_df)
                    
                    # Store for plotting
                    st.session_state['prediction_data'] = pred_df
                    st.session_state['stock_symbol'] = stock_symbol
                    
                else:
                    st.error(f"API Error: {response.status_code} - {response.text}")
                    
            except Exception as e:
                st.error(f"Error calling API: {str(e)}")

with col2:
    st.subheader("📈 Prediction Chart")
    
    if 'prediction_data' in st.session_state:
        # Create prediction chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=st.session_state['prediction_data']['date'],
            y=st.session_state['prediction_data']['predicted_price'],
            mode='lines+markers',
            name=f'{st.session_state["stock_symbol"]} Predictions',
            line=dict(color='blue', width=2),
            marker=dict(size=6)
        ))
        
        # Add confidence intervals if available
        if 'lower_bound' in st.session_state['prediction_data'].columns:
            fig.add_trace(go.Scatter(
                x=st.session_state['prediction_data']['date'],
                y=st.session_state['prediction_data']['upper_bound'],
                fill=None,
                mode='lines',
                line=dict(width=0),
                showlegend=False
            ))
            
            fig.add_trace(go.Scatter(
                x=st.session_state['prediction_data']['date'],
                y=st.session_state['prediction_data']['lower_bound'],
                fill='tonexty',
                mode='lines',
                line=dict(width=0),
                name='Confidence Interval',
                fillcolor='rgba(0,100,80,0.2)'
            ))
        
        fig.update_layout(
            title=f'{st.session_state["stock_symbol"]} Price Predictions',
            xaxis_title='Date',
            yaxis_title='Price ($)',
            hovermode='x unified',
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Download button
        csv = st.session_state['prediction_data'].to_csv(index=False)
        st.download_button(
            label="📥 Download Predictions as CSV",
            data=csv,
            file_name=f"{st.session_state['stock_symbol']}_predictions.csv",
            mime="text/csv"
        )
    else:
        st.info("Click 'Predict' button to see the chart")

# Model Performance Section
st.header("📊 Model Performance")

try:
    response = requests.get(f"{API_BASE_URL}/performance")
    if response.status_code == 200:
        performance = response.json()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Validation Loss", f"{performance.get('val_loss', 'N/A'):.4f}")
        with col2:
            st.metric("Validation MAE", f"{performance.get('val_mae', 'N/A'):.4f}")
        with col3:
            st.metric("Training Loss", f"{performance.get('train_loss', 'N/A'):.4f}")
    else:
        st.warning("Performance metrics not available")
except:
    st.warning("Could not fetch performance metrics")

# Available Stocks Section
st.header("📋 Available Stocks")

try:
    response = requests.get(f"{API_BASE_URL}/stocks")
    if response.status_code == 200:
        stocks_data = response.json()
        
        if isinstance(stocks_data, dict) and 'stocks' in stocks_data:
            stocks = stocks_data['stocks']
        else:
            stocks = stocks_data
            
        for stock in stocks:
            st.info(f"✅ {stock}")
    else:
        st.warning("Stock list not available")
except:
    st.warning("Could not fetch stock list")

# API Documentation Link
st.markdown("---")
st.markdown("### 📚 API Documentation")
st.markdown(f"- [Swagger UI]({API_BASE_URL}/docs)")
st.markdown(f"- [ReDoc]({API_BASE_URL}/redoc)")

# Auto-refresh option
if st.sidebar.checkbox("Auto-refresh predictions"):
    st.sidebar.info("Dashboard will refresh every 30 seconds")
    st.experimental_rerun()