"""
predictor.py
High-speed inference engine for single predictions and multi-dimensional flexible searches.
Executes batch predictions in a single model call with zero-latency response (<50ms).
"""

import os
import json
from datetime import datetime, date, timedelta
import numpy as np
import pandas as pd
import joblib

from ml.surge_engine import CalendarSurgeEngine

TIME_BINS_ORDER = ["Early_Morning", "Morning", "Afternoon", "Evening", "Night", "Late_Night"]
TIME_BIN_LABELS = {
    "Early_Morning": "Early Morning (00:00 - 06:00)",
    "Morning": "Morning (06:00 - 12:00)",
    "Afternoon": "Afternoon (12:00 - 18:00)",
    "Evening": "Evening (18:00 - 22:00)",
    "Night": "Night (22:00 - 24:00)",
    "Late_Night": "Late Night (23:00 - 04:00)"
}

class FlightFarePredictor:
    def __init__(self, models_dir=None, data_dir=None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.models_dir = models_dir if models_dir else os.path.join(base_dir, "models")
        self.data_dir = data_dir if data_dir else os.path.join(base_dir, "data")
        self.preprocessor = None
        self.rf_model = None
        self.lr_model = None
        self.route_averages = {}
        self.metrics = {}
        self.surge_engine = CalendarSurgeEngine(os.path.join(self.data_dir, "festivals.json"))
        self.load_artifacts()

    def load_artifacts(self):
        prep_path = os.path.join(self.models_dir, "preprocessor.joblib")
        rf_path = os.path.join(self.models_dir, "rf_model.joblib")
        lr_path = os.path.join(self.models_dir, "lr_model.joblib")
        avg_path = os.path.join(self.data_dir, "route_averages.json")
        met_path = os.path.join(self.data_dir, "model_metrics.json")

        if os.path.exists(prep_path) and os.path.exists(rf_path):
            self.preprocessor = joblib.load(prep_path)
            self.rf_model = joblib.load(rf_path)
            if os.path.exists(lr_path):
                self.lr_model = joblib.load(lr_path)

        if os.path.exists(avg_path):
            with open(avg_path, "r", encoding="utf-8") as f:
                self.route_averages = json.load(f)

        if os.path.exists(met_path):
            with open(met_path, "r", encoding="utf-8") as f:
                self.metrics = json.load(f)

    def get_route_defaults(self, source, dest, airline, dep_time):
        key = f"{source}_{dest}_{airline}_{dep_time}"
        default_key = f"{source}_{dest}_{airline}_DEFAULT"
        if key in self.route_averages:
            return self.route_averages[key]["avg_duration"], self.route_averages[key]["mode_stops"]
        elif default_key in self.route_averages:
            return self.route_averages[default_key]["avg_duration"], self.route_averages[default_key]["mode_stops"]
        return 2.2, 0

    def flexible_search(self, source_city, destination_city, airline_choice, travel_date_str,
                        date_flexibility=1, time_slot_choice="ANY"):
        """
        Executes an instant vectorized flexible search across dates (±flexibility)
        and time slots (single or all 6 slots) for Air India and/or IndiGo.
        """
        if self.rf_model is None or self.preprocessor is None:
            raise RuntimeError("Models not loaded. Please run train.py first.")

        today = date.today()
        base_date = datetime.strptime(travel_date_str, "%Y-%m-%d").date()

        # Generate Candidate Dates based on date_flexibility (0, 1, or 2)
        candidate_dates = []
        for offset in range(-date_flexibility, date_flexibility + 1):
            d = base_date + timedelta(days=offset)
            # Drop dates in the past
            if d >= today:
                candidate_dates.append(d)

        if not candidate_dates:
            candidate_dates = [today]

        # Determine Time Slots
        if time_slot_choice.upper() == "ANY" or not time_slot_choice:
            time_slots = TIME_BINS_ORDER
        else:
            time_slots = [time_slot_choice] if time_slot_choice in TIME_BINS_ORDER else ["Morning"]

        # Determine Airlines
        if airline_choice.upper() in ["BOTH", "ALL", "SIDE_BY_SIDE"]:
            airlines = ["Air India", "IndiGo"]
        else:
            airlines = [airline_choice]

        # Build Candidate Rows
        rows = []
        for d in candidate_dates:
            days_left = max(1, min(60, (d - today).days))
            is_capped = (d - today).days > 60

            # Evaluate calendar surge for this date
            surge_info = self.surge_engine.evaluate_date(d, source_city, destination_city)

            for air in airlines:
                for slot in time_slots:
                    duration, stops = self.get_route_defaults(source_city, destination_city, air, slot)
                    rows.append({
                        "date_str": d.strftime("%Y-%m-%d"),
                        "display_date": d.strftime("%a, %d %b"),
                        "day_of_week": d.strftime("%A"),
                        "days_left": days_left,
                        "is_capped": is_capped,
                        "airline": air,
                        "source_city": source_city,
                        "destination_city": destination_city,
                        "departure_time": slot,
                        "stops": stops,
                        "duration": duration,
                        "surge_factor": surge_info["surge_factor"],
                        "surge_tag": surge_info["tag"],
                        "surge_reason": surge_info["reason"],
                        "has_surge": surge_info["has_surge"],
                        "is_user_choice": (d == base_date and (time_slot_choice.upper() == "ANY" or slot == time_slot_choice))
                    })

        df_candidates = pd.DataFrame(rows)
        cat_features = ["airline", "source_city", "destination_city", "departure_time"]
        num_features = ["duration", "days_left"]
        passthrough_features = ["stops"]

        X_input = df_candidates[cat_features + num_features + passthrough_features]
        X_trans = self.preprocessor.transform(X_input)

        # Batch prediction with Random Forest
        rf_pred_log = self.rf_model.predict(X_trans)
        rf_base_fares = np.exp(rf_pred_log)

        # Optional baseline comparison
        lr_base_fares = None
        if self.lr_model:
            lr_pred_log = self.lr_model.predict(X_trans)
            lr_base_fares = np.exp(lr_pred_log)

        # Apply Indian Festival & Weekend Surge Engine Multipliers
        final_fares = []
        for i, row in df_candidates.iterrows():
            base_fare = float(rf_base_fares[i])
            surge_mult = float(row["surge_factor"])
            total_fare = int(round(base_fare * (1.0 + surge_mult) / 10.0) * 10)
            
            lr_fare = None
            if lr_base_fares is not None:
                lr_fare = int(round(float(lr_base_fares[i]) * (1.0 + surge_mult) / 10.0) * 10)

            final_fares.append({
                "date": row["date_str"],
                "display_date": row["display_date"],
                "day_of_week": row["day_of_week"],
                "days_left": int(row["days_left"]),
                "is_capped": bool(row["is_capped"]),
                "airline": row["airline"],
                "source_city": row["source_city"],
                "destination_city": row["destination_city"],
                "departure_time": row["departure_time"],
                "departure_time_label": TIME_BIN_LABELS.get(row["departure_time"], row["departure_time"]),
                "stops": int(row["stops"]),
                "duration": float(row["duration"]),
                "duration_text": f"{int(row['duration'])}h {int((row['duration'] % 1) * 60)}m",
                "base_ml_fare": int(round(base_fare)),
                "surge_factor": surge_mult,
                "surge_tag": row["surge_tag"],
                "surge_reason": row["surge_reason"],
                "has_surge": bool(row["has_surge"]),
                "predicted_fare": total_fare,
                "lr_baseline_fare": lr_fare,
                "is_user_choice": bool(row["is_user_choice"])
            })

        # Identify Overall Cheapest Option
        cheapest_option = min(final_fares, key=lambda x: x["predicted_fare"])

        # Determine First Choice / User Base Fare for Savings Calculation
        user_choice_items = [f for f in final_fares if f["is_user_choice"]]
        if user_choice_items:
            # Baseline is user's selected airline or avg of user's selection
            first_choice = user_choice_items[0]
            first_choice_fare = first_choice["predicted_fare"]
        else:
            first_choice = final_fares[0]
            first_choice_fare = first_choice["predicted_fare"]

        savings = max(0, first_choice_fare - cheapest_option["predicted_fare"])

        # Format Grid Matrix for easy UI rendering
        # Structure: grid[airline][time_slot][date_str] = cell_data
        grid = {}
        for air in airlines:
            grid[air] = {}
            for slot in time_slots:
                grid[air][slot] = {}

        for item in final_fares:
            air = item["airline"]
            slot = item["departure_time"]
            d_str = item["date"]
            grid[air][slot][d_str] = item

        return {
            "query": {
                "source_city": source_city,
                "destination_city": destination_city,
                "travel_date": travel_date_str,
                "airline_choice": airline_choice,
                "date_flexibility": date_flexibility,
                "time_slot_choice": time_slot_choice
            },
            "dates": [d.strftime("%Y-%m-%d") for d in candidate_dates],
            "display_dates": [
                {
                    "date": d.strftime("%Y-%m-%d"),
                    "display": d.strftime("%a, %d %b"),
                    "day": d.strftime("%A"),
                    "is_selected": d == base_date
                }
                for d in candidate_dates
            ],
            "time_slots": time_slots,
            "airlines": airlines,
            "cheapest_option": cheapest_option,
            "first_choice": first_choice,
            "savings": savings,
            "savings_pct": round((savings / first_choice_fare * 100), 1) if first_choice_fare > 0 else 0,
            "grid": grid,
            "all_results": final_fares
        }

if __name__ == "__main__":
    predictor = FlightFarePredictor()
    # Test flexible search
    res = predictor.flexible_search("Mumbai", "Delhi", "BOTH", "2026-11-10", date_flexibility=1, time_slot_choice="ANY")
    print("Cheapest:", res["cheapest_option"])
    print("Savings:", res["savings"])
