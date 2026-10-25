# AeroPredict: Flight Price Prediction & Flexible Fare Search

An intelligent Machine Learning web application predicting domestic airfares for **Air India** and **IndiGo** between **Mumbai (BOM)**, **Delhi (DEL)**, and **Bengaluru (BLR)**.

Featuring a **Flexible Fare Matrix** (date shifting up to $\pm 2$ days and all departure time slots), side-by-side carrier comparisons, and a **Hybrid Indian Aviation Calendar Surge Engine** (adjusting for Diwali, Holi, national holidays, and long weekends).

---

## 🚀 Key Features

1. **Flexible Fare Matrix ($\pm 1$ or $\pm 2$ Days & Time Slots):**
   - Automatically builds candidate rows for all combinations in a single vectorized inference call ($<50$ms).
   - Generates an interactive visual heatmap table highlighting the absolute cheapest flight and showing exact rupee savings versus the user's primary selection.

2. **Side-by-Side Carrier Comparison:**
   - Displays Air India (Full-Service Carrier) alongside IndiGo (Low-Cost Carrier) with baseline metrics, duration, and inclusions.

3. **Hybrid Indian Festival & Long Weekend Surge Engine:**
   - Evaluates the user's travel date against Indian gazetted holidays (Diwali Week, Holi, Durga Puja/Dussehra, Eid, Christmas/New Year, Republic Day, Independence Day, Gandhi Jayanti).
   - Dynamically adds a transparent demand surcharge (+15% to +45%) to the base Random Forest prediction.
   - Detects standard weekend spikes (Friday evening, Sunday return rush, Monday morning corporate).

4. **3-Month Observational Lookback & 80% Recency Weighting:**
   - Uses time-decay sample weighting: $w_i = \exp(-\lambda \cdot \Delta t)$, concentrating 80% of aggregate weight on the most recent 30-day observations of the 3-month window.
   - Prediction horizon is calibrated and capped at 60 days (2 months ahead).

---

## 📊 Model Benchmarks & Validation

Evaluated on an independent 80/20 train/test split:

| Metric | Linear Regression (Baseline) | Tuned Random Forest (Core Model) | Improvement |
| :--- | :--- | :--- | :--- |
| **MAE (Mean Absolute Error)** | ₹409.96 | **₹269.56** | **34.2% reduction in error** |
| **RMSE (Root Mean Squared Error)**| ₹589.61 | **₹356.47** | **39.5% reduction** |
| **$R^2$ (Variance Explained)** | 0.8183 | **0.9336** | **Captures 93.4% of variance** |
| **MAPE (%)** | 7.10% | **4.87%** | Sub-5% percentage error |

### Feature Importance Breakdown:
1. `days_left` (Lead time curve): **41.2%**
2. `airline` (Air India vs IndiGo pricing base): **21.8%**
3. `duration` (Flight flight time / route length): **18.4%**
4. `departure_time` (Morning/Evening peak slots): **12.1%**
5. `stops` (Direct vs 1-stop): **6.5%**

---

## 🛠️ Project Structure

```
PA/
├── data/
│   ├── dataset_builder.py    # Generates 3-month calibrated dataset with time decay weights
│   ├── festivals.json        # 2026-2027 Indian festival, holiday, and weekend surge schedule
│   ├── flight_prices.csv     # 35,000 flight records
│   ├── model_metrics.json    # Evaluated benchmark statistics and feature importances
│   └── route_averages.json   # Route/airline lookup tables for zero-latency parameter filling
├── ml/
│   ├── surge_engine.py       # CalendarSurgeEngine for holiday/long weekend surge calculation
│   ├── train.py              # ML pipeline training Linear Regression & Random Forest
│   └── predictor.py          # Vectorized flexible search & inference engine
├── models/
│   ├── preprocessor.joblib   # Fitted OneHotEncoder & StandardScaler pipeline
│   ├── rf_model.joblib       # Tuned Random Forest Regressor
│   └── lr_model.joblib       # Baseline Linear Regression model
├── server/
│   └── app.py               # FastAPI REST server exposing search, metrics & calendar APIs
├── static/
│   ├── index.html            # Modern glassmorphism UI with side-by-side & heatmap matrix
│   ├── style.css             # Rich dark mode vanilla CSS with micro-animations
│   └── app.js                # Interactive client logic and API integration
└── README.md
```

---

## 💻 Running Locally

### 1. Start the FastAPI Development Server:
```bash
python -m uvicorn server.app:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Open the Web Application:
Navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000) in your web browser.
