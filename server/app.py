"""
app.py
FastAPI backend server for the Flight Price Prediction Website.
Exposes REST endpoints for model inference, flexible date/time search,
calendar surge evaluation, and model metrics comparison.
"""

import os
from datetime import datetime, date
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from ml.predictor import FlightFarePredictor, TIME_BINS_ORDER, TIME_BIN_LABELS

app = FastAPI(
    title="Flight Price Prediction API",
    description="Random Forest Flight Fare Predictor with Flexible Search Grid & Calendar Surge Engine",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

predictor = FlightFarePredictor()

class FlexibleSearchRequest(BaseModel):
    source_city: str = Field(..., example="Mumbai")
    destination_city: str = Field(..., example="Delhi")
    airline_choice: str = Field(default="BOTH", example="BOTH") # "Air India", "IndiGo", or "BOTH"
    travel_date: str = Field(..., example="2026-11-10")
    date_flexibility: int = Field(default=1, ge=0, le=2) # 0 = exact, 1 = +-1 day, 2 = +-2 days
    time_slot_choice: str = Field(default="ANY") # "ANY" or specific bin name

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "models_loaded": predictor.rf_model is not None,
        "supported_routes": ["Mumbai (BOM)", "Delhi (DEL)", "Bengaluru (BLR)"],
        "supported_airlines": ["Air India", "IndiGo"],
        "max_horizon_days": 60,
        "sample_weight_policy": "80% mass on recent 30-day observations of 3-month window"
    }

@app.get("/api/routes")
def get_routes_and_options():
    return {
        "airports": [
            {"code": "BOM", "city": "Mumbai", "name": "Chhatrapati Shivaji Maharaj Intl"},
            {"code": "DEL", "city": "Delhi", "name": "Indira Gandhi Intl"},
            {"code": "BLR", "city": "Bangalore", "name": "Kempegowda Intl"}
        ],
        "routes": [
            {"from": "Mumbai", "to": "Delhi", "route_name": "BOM -> DEL", "base_time": "2h 15m"},
            {"from": "Delhi", "to": "Mumbai", "route_name": "DEL -> BOM", "base_time": "2h 15m"},
            {"from": "Mumbai", "to": "Bangalore", "route_name": "BOM -> BLR", "base_time": "1h 45m"},
            {"from": "Bangalore", "to": "Mumbai", "route_name": "BLR -> BOM", "base_time": "1h 45m"},
            {"from": "Delhi", "to": "Bangalore", "route_name": "DEL -> BLR", "base_time": "2h 45m"},
            {"from": "Bangalore", "to": "Delhi", "route_name": "BLR -> DEL", "base_time": "2h 45m"}
        ],
        "airlines": [
            {"id": "BOTH", "name": "Compare Both (Air India & IndiGo)", "badge": "Side-by-Side"},
            {"id": "Air India", "name": "Air India", "badge": "Full-Service"},
            {"id": "IndiGo", "name": "IndiGo", "badge": "Low-Cost"}
        ],
        "time_slots": [
            {"id": "ANY", "label": "Any Time of Day", "desc": "Search all 6 departure slots"},
            {"id": "Early_Morning", "label": "Early Morning (00:00 - 06:00)", "desc": "Red-eye & dawn flights"},
            {"id": "Morning", "label": "Morning (06:00 - 12:00)", "desc": "Prime business slots"},
            {"id": "Afternoon", "label": "Afternoon (12:00 - 18:00)", "desc": "Midday departures"},
            {"id": "Evening", "label": "Evening (18:00 - 22:00)", "desc": "Prime evening slots"},
            {"id": "Night", "label": "Night (22:00 - 24:00)", "desc": "Late departures"},
            {"id": "Late_Night", "label": "Late Night (23:00 - 04:00)", "desc": "Night economy flights"}
        ],
        "flexibility_options": [
            {"value": 0, "label": "Exact Date", "desc": "1 date"},
            {"value": 1, "label": "±1 Day Flexibility", "desc": "3 dates (Best balance)"},
            {"value": 2, "label": "±2 Days Flexibility", "desc": "5 dates (Maximum savings)"}
        ]
    }

@app.post("/api/flexible-search")
def run_flexible_search(req: FlexibleSearchRequest):
    if req.source_city == req.destination_city:
        raise HTTPException(status_code=400, detail="Source and destination cities must be different.")
    
    valid_cities = ["Mumbai", "Delhi", "Bangalore"]
    if req.source_city not in valid_cities or req.destination_city not in valid_cities:
        raise HTTPException(status_code=400, detail=f"Cities must be among {valid_cities}")

    try:
        results = predictor.flexible_search(
            source_city=req.source_city,
            destination_city=req.destination_city,
            airline_choice=req.airline_choice,
            travel_date_str=req.travel_date,
            date_flexibility=req.date_flexibility,
            time_slot_choice=req.time_slot_choice
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics")
def get_model_metrics():
    return predictor.metrics

@app.get("/api/festivals")
def get_festival_calendar():
    return {
        "festivals": predictor.surge_engine.festivals,
        "weekend_surges": predictor.surge_engine.weekend_weights
    }

# Mount static files
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_index():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Flight Price Prediction API is active. UI static files being created."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.app:app", host="127.0.0.1", port=8000, reload=True)
