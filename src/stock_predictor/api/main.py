"""FastAPI application."""
from fastapi import FastAPI
from .routers import predict
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="Global Stock Predictor API",
    version="0.1.0",
    description="LSTM-based stock price prediction API for global markets"
)

# Add CORS middleware for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your dashboard URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router)

@app.get("/")
def root():
    return {
        "message": "Global Stock Predictor API is running",
        "version": "0.1.0",
        "status": "active",
        "markets": ["US", "Kenya", "Nigeria", "South Africa"]
    }

@app.get("/health")
def health():
    return {"status": "healthy"}