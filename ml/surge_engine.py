"""
surge_engine.py
Indian Aviation Calendar & Holiday Surge Pricing Engine.
Calculates festival, national holiday, and long weekend demand multipliers
for given travel dates and metro corridor pairs.
"""

import json
import os
from datetime import datetime, date

FESTIVALS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "festivals.json")

class CalendarSurgeEngine:
    def __init__(self, config_path=FESTIVALS_FILE):
        self.config_path = config_path
        self.festivals = []
        self.weekend_weights = {}
        self.load_config()

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.festivals = data.get("festivals", [])
                self.weekend_weights = data.get("weekendSurge", {})
        else:
            self.festivals = []
            self.weekend_weights = {
                "friday": 0.12,
                "saturday": 0.08,
                "sunday": 0.18,
                "mondayMorning": 0.15
            }

    def evaluate_date(self, travel_date, source_city=None, destination_city=None, departure_slot=None):
        """
        Evaluates a travel date (string 'YYYY-MM-DD' or date object).
        Returns surge details: factor (e.g. 0.35), tag, description, is_surge.
        """
        if isinstance(travel_date, str):
            dt = datetime.strptime(travel_date, "%Y-%m-%d").date()
        elif isinstance(travel_date, datetime):
            dt = travel_date.date()
        else:
            dt = travel_date

        weekday_idx = dt.weekday() # 0 = Monday, 6 = Sunday
        day_name = dt.strftime("%A")

        # 1. Check Festival Matches
        matched_festivals = []
        for fest in self.festivals:
            start_dt = datetime.strptime(fest["startDate"], "%Y-%m-%d").date()
            end_dt = datetime.strptime(fest["endDate"], "%Y-%m-%d").date()
            if start_dt <= dt <= end_dt:
                matched_festivals.append(fest)

        if matched_festivals:
            # Pick highest surge among overlapping festivals
            top_fest = max(matched_festivals, key=lambda x: x["surgeFactor"])
            surge_factor = top_fest["surgeFactor"]
            
            # Additional corridor boost (e.g., Ganesh Chaturthi in Mumbai, Durga Puja in major metros)
            if "Maharashtra" in top_fest.get("description", "") and (source_city == "Mumbai" or destination_city == "Mumbai"):
                surge_factor += 0.05
                
            return {
                "has_surge": True,
                "surge_factor": round(surge_factor, 2),
                "surge_pct": f"+{int(round(surge_factor * 100))}%",
                "tag": top_fest["tag"],
                "reason": top_fest["description"],
                "type": "festival",
                "festival_name": top_fest["name"],
                "day_name": day_name
            }

        # 2. Check Weekend Surge
        # Friday (4), Saturday (5), Sunday (6), Monday (0)
        surge_factor = 0.0
        reason = None
        tag = None

        if weekday_idx == 4: # Friday evening rush
            surge_factor = self.weekend_weights.get("friday", 0.12)
            tag = "Weekend Outbound Rush"
            reason = "Friday departure demand surge across business metros"
        elif weekday_idx == 6: # Sunday return rush
            surge_factor = self.weekend_weights.get("sunday", 0.18)
            tag = "Sunday Homecoming Rush"
            reason = "Peak Sunday return flights with high load factor"
        elif weekday_idx == 5: # Saturday
            surge_factor = self.weekend_weights.get("saturday", 0.08)
            tag = "Saturday Leisure Travel"
            reason = "Moderate weekend leisure load"
        elif weekday_idx == 0 and departure_slot in ["Early_Morning", "Morning"]:
            surge_factor = self.weekend_weights.get("mondayMorning", 0.15)
            tag = "Monday Morning Business Surge"
            reason = "High-priority corporate travelers between BOM, DEL, and BLR"

        if surge_factor > 0:
            return {
                "has_surge": True,
                "surge_factor": round(surge_factor, 2),
                "surge_pct": f"+{int(round(surge_factor * 100))}%",
                "tag": tag,
                "reason": reason,
                "type": "weekend",
                "festival_name": None,
                "day_name": day_name
            }

        return {
            "has_surge": False,
            "surge_factor": 0.0,
            "surge_pct": "0%",
            "tag": "Standard Base Fare",
            "reason": "Mid-week non-peak schedule (ML base rate)",
            "type": "standard",
            "festival_name": None,
            "day_name": day_name
        }

if __name__ == "__main__":
    engine = CalendarSurgeEngine()
    print("Diwali test:", engine.evaluate_date("2026-11-10", "Mumbai", "Delhi"))
    print("Sunday test:", engine.evaluate_date("2026-10-18", "Bangalore", "Delhi"))
    print("Regular Wednesday test:", engine.evaluate_date("2026-10-21", "Mumbai", "Delhi"))
