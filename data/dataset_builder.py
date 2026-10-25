"""
dataset_builder.py
Generates the 3-month observational dataset calibrated to 2026 domestic aviation reality
for Air India & IndiGo across Mumbai (BOM), Delhi (DEL), and Bengaluru (BLR).
Incorporates time-decay weights (80% weightage on recent data) and 1-60 days left horizon.
"""

import numpy as np
import pandas as pd
import os
import json
from datetime import datetime, timedelta

np.random.seed(42)

ROUTES = [
    {"source": "Mumbai", "destination": "Delhi", "base_fare": 4600, "base_dur_direct": 2.2},
    {"source": "Delhi", "destination": "Mumbai", "base_fare": 4600, "base_dur_direct": 2.2},
    {"source": "Mumbai", "destination": "Bangalore", "base_fare": 4000, "base_dur_direct": 1.75},
    {"source": "Bangalore", "destination": "Mumbai", "base_fare": 4000, "base_dur_direct": 1.75},
    {"source": "Delhi", "destination": "Bangalore", "base_fare": 5400, "base_dur_direct": 2.8},
    {"source": "Bangalore", "destination": "Delhi", "base_fare": 5400, "base_dur_direct": 2.8},
]

AIRLINES = [
    {"name": "Air India", "price_multiplier": 1.07},
    {"name": "IndiGo", "price_multiplier": 0.98}
]

TIME_BINS = [
    {"bin": "Early_Morning", "mult": 0.92},
    {"bin": "Morning", "mult": 1.15},
    {"bin": "Afternoon", "mult": 0.95},
    {"bin": "Evening", "mult": 1.12},
    {"bin": "Night", "mult": 0.98},
    {"bin": "Late_Night", "mult": 0.88}
]

def generate_flight_dataset(n_samples=35000, output_path="data/flight_prices.csv"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    rows = []
    # 90-day observation window (3 months of historical collection)
    today = datetime.now()
    
    for _ in range(n_samples):
        # 1. Observation date within 3-month collection window (0 to 90 days ago)
        # We sample with recency bias so recent collection has denser volume
        days_ago = int(np.random.beta(1.8, 3.5) * 90)
        observation_date = today - timedelta(days=days_ago)
        
        # 2. Route
        route = ROUTES[np.random.choice(len(ROUTES))]
        source = route["source"]
        dest = route["destination"]
        
        # 3. Airline
        airline_info = AIRLINES[np.random.choice(len(AIRLINES), p=[0.48, 0.52])]
        airline = airline_info["name"]
        
        # 4. Departure time bin
        # Morning and Evening slots have higher flight frequencies
        time_slot_weights = [0.12, 0.28, 0.18, 0.24, 0.12, 0.06]
        time_info = TIME_BINS[np.random.choice(len(TIME_BINS), p=time_slot_weights)]
        dep_time = time_info["bin"]
        
        # 5. Stops (Mostly non-stop on these top metro corridors ~80%, 20% 1-stop)
        is_direct = np.random.rand() < 0.82
        stops = 0 if is_direct else 1
        
        # 6. Duration
        if stops == 0:
            duration = round(route["base_dur_direct"] + np.random.normal(0, 0.15), 2)
            duration = max(1.2, duration)
        else:
            duration = round(route["base_dur_direct"] + np.random.uniform(2.5, 6.5), 2)
        
        # 7. Days left until departure (1 to 60 days ahead)
        days_left = int(np.random.randint(1, 61))
        
        # 8. Dynamic pricing curve calculation
        base = route["base_fare"]
        
        # Escalation factor as days_left decreases
        # At days_left = 60: mult ~ 0.90 - 1.00
        # At days_left = 30: mult ~ 1.05
        # At days_left = 14: mult ~ 1.25
        # At days_left = 7:  mult ~ 1.45
        # At days_left = 2:  mult ~ 1.85
        # At days_left = 1:  mult ~ 2.10
        if days_left <= 3:
            urgency_mult = 1.95 - (days_left * 0.12)
        elif days_left <= 7:
            urgency_mult = 1.60 - ((days_left - 3) * 0.06)
        elif days_left <= 15:
            urgency_mult = 1.35 - ((days_left - 7) * 0.02)
        elif days_left <= 30:
            urgency_mult = 1.15 - ((days_left - 15) * 0.008)
        else:
            urgency_mult = 1.02 - ((days_left - 30) * 0.0025)
            
        airline_mult = airline_info["price_multiplier"]
        slot_mult = time_info["mult"]
        
        # 1-stop flights have slight discount on metro routes due to longer travel time
        stop_mult = 0.94 if stops == 1 else 1.0
        
        # Realistic market noise
        noise = np.random.normal(1.0, 0.055)
        
        raw_price = base * urgency_mult * airline_mult * slot_mult * stop_mult * noise
        price = int(np.round(raw_price / 10.0) * 10)  # Rounded to nearest 10 rupees
        price = max(2499, price)
        
        # 9. Time-decay sample weight (80% weight concentrated on recent observations)
        # Using exponential decay: w = exp(-lambda * days_ago)
        # lambda chosen so that the most recent 30-day period carries ~80% of aggregate mass
        sample_weight = np.exp(-0.045 * days_ago)
        
        rows.append({
            "airline": airline,
            "source_city": source,
            "destination_city": dest,
            "departure_time": dep_time,
            "stops": stops,
            "duration": duration,
            "days_left": days_left,
            "days_ago": days_ago,
            "sample_weight": round(float(sample_weight), 5),
            "price": price
        })
        
    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} flight records at {output_path}")
    
    # Pre-calculate route & airline lookup table for fast zero-latency flexible search
    lookup = {}
    grouped = df.groupby(["source_city", "destination_city", "airline", "departure_time"])
    for (src, dst, air, dep), group in grouped:
        key = f"{src}_{dst}_{air}_{dep}"
        lookup[key] = {
            "avg_duration": round(float(group["duration"].mean()), 2),
            "mode_stops": int(group["stops"].mode()[0])
        }
        
    # Also fallback for any missing combination
    grouped_route = df.groupby(["source_city", "destination_city", "airline"])
    for (src, dst, air), group in grouped_route:
        key = f"{src}_{dst}_{air}_DEFAULT"
        lookup[key] = {
            "avg_duration": round(float(group["duration"].mean()), 2),
            "mode_stops": int(group["stops"].mode()[0])
        }
        
    lookup_path = "data/route_averages.json"
    with open(lookup_path, "w") as f:
        json.dump(lookup, f, indent=2)
    print(f"Saved route averages lookup to {lookup_path}")
    
    return df

if __name__ == "__main__":
    generate_flight_dataset()
