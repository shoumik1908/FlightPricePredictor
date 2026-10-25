"""
train.py
Model training pipeline for Flight Price Prediction.
Trains a Linear Regression baseline and a tuned Random Forest Regressor on log(price)
using time-decay sample weighting (80% weight on recent 30-day observations).
Saves trained models, preprocessor, and comprehensive evaluation metrics.
"""

import os
import json
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from data.dataset_builder import generate_flight_dataset

def calculate_mape(y_true, y_pred):
    return float(np.mean(np.abs((y_true - y_pred) / y_true)) * 100)

def train_and_evaluate():
    data_path = os.path.join("data", "flight_prices.csv")
    if not os.path.exists(data_path):
        print("Data file not found. Generating calibrated dataset...")
        df = generate_flight_dataset(n_samples=35000, output_path=data_path)
    else:
        df = pd.read_csv(data_path)

    print(f"Loaded {len(df)} flight records.")
    
    # Feature columns
    cat_features = ["airline", "source_city", "destination_city", "departure_time"]
    num_features = ["duration", "days_left"]
    passthrough_features = ["stops"]
    
    X = df[cat_features + num_features + passthrough_features]
    y_raw = df["price"].values
    y_log = np.log(y_raw)
    weights = df["sample_weight"].values
    
    # 80/20 train/test holdout split
    X_train, X_test, y_train_log, y_test_log, y_train_raw, y_test_raw, w_train, w_test = train_test_split(
        X, y_log, y_raw, weights, test_size=0.20, random_state=42
    )
    
    print(f"Training split: {len(X_train)} samples, Test split: {len(X_test)} samples")
    
    # Preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore"), cat_features),
            ("num", StandardScaler(), num_features),
            ("pass", "passthrough", passthrough_features)
        ]
    )
    
    X_train_trans = preprocessor.fit_transform(X_train)
    X_test_trans = preprocessor.transform(X_test)
    
    # Get transformed feature names
    cat_encoder = preprocessor.named_transformers_["cat"]
    encoded_cat_names = list(cat_encoder.get_feature_names_out(cat_features))
    all_feature_names = encoded_cat_names + num_features + passthrough_features
    
    # 1. Baseline Model: Linear Regression
    print("Training Baseline Model (Linear Regression)...")
    lr = LinearRegression()
    lr.fit(X_train_trans, y_train_log, sample_weight=w_train)
    
    lr_pred_log = lr.predict(X_test_trans)
    lr_pred_raw = np.exp(lr_pred_log)
    
    lr_mae = float(mean_absolute_error(y_test_raw, lr_pred_raw))
    lr_rmse = float(np.sqrt(mean_squared_error(y_test_raw, lr_pred_raw)))
    lr_r2 = float(r2_score(y_test_raw, lr_pred_raw))
    lr_mape = calculate_mape(y_test_raw, lr_pred_raw)
    
    import sys
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    print(f"Linear Regression Baseline -> MAE: INR {lr_mae:.2f}, RMSE: INR {lr_rmse:.2f}, R2: {lr_r2:.4f}, MAPE: {lr_mape:.2f}%")
    
    # 2. Challenger Model: Tuned Random Forest Regressor
    print("Training Tuned Random Forest Regressor...")
    rf = RandomForestRegressor(
        n_estimators=120,
        min_samples_leaf=3,
        max_features="sqrt",
        random_state=42,
        n_jobs=-1
    )
    rf.fit(X_train_trans, y_train_log, sample_weight=w_train)
    
    rf_pred_log = rf.predict(X_test_trans)
    rf_pred_raw = np.exp(rf_pred_log)
    
    rf_mae = float(mean_absolute_error(y_test_raw, rf_pred_raw))
    rf_rmse = float(np.sqrt(mean_squared_error(y_test_raw, rf_pred_raw)))
    rf_r2 = float(r2_score(y_test_raw, rf_pred_raw))
    rf_mape = calculate_mape(y_test_raw, rf_pred_raw)
    
    print(f"Random Forest Regressor -> MAE: INR {rf_mae:.2f}, RMSE: INR {rf_rmse:.2f}, R2: {rf_r2:.4f}, MAPE: {rf_mape:.2f}%")
    
    # Check target: Forest beats Linear Regression
    mae_improvement = ((lr_mae - rf_mae) / lr_mae) * 100
    print(f"Target Check: Random Forest beats Linear Regression MAE by {mae_improvement:.1f}%!")
    
    # Stratified Error by Airline
    airline_metrics = {}
    for air in ["Air India", "IndiGo"]:
        idx = X_test["airline"] == air
        air_true = y_test_raw[idx]
        air_pred_rf = rf_pred_raw[idx]
        air_pred_lr = lr_pred_raw[idx]
        airline_metrics[air] = {
            "samples": int(np.sum(idx)),
            "rf_mae": round(float(mean_absolute_error(air_true, air_pred_rf)), 2),
            "rf_mape": round(calculate_mape(air_true, air_pred_rf), 2),
            "lr_mae": round(float(mean_absolute_error(air_true, air_pred_lr)), 2),
            "avg_fare": round(float(np.mean(air_true)), 2)
        }
        
    # Feature Importances
    importances = rf.feature_importances_
    sorted_idx = np.argsort(importances)[::-1]
    feature_imp = [
        {"feature": all_feature_names[i], "importance": round(float(importances[i]), 4)}
        for i in sorted_idx
    ]
    
    # Save Models and Artifacts
    os.makedirs("models", exist_ok=True)
    joblib.dump(preprocessor, "models/preprocessor.joblib")
    joblib.dump(rf, "models/rf_model.joblib")
    joblib.dump(lr, "models/lr_model.joblib")
    print("Models and preprocessor saved to models/ directory.")
    
    metrics_summary = {
        "generated_at": pd.Timestamp.now().isoformat(),
        "total_records": len(df),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "models": {
            "linear_regression": {
                "name": "Linear Regression (Baseline)",
                "mae": round(lr_mae, 2),
                "rmse": round(lr_rmse, 2),
                "r2": round(lr_r2, 4),
                "mape": round(lr_mape, 2)
            },
            "random_forest": {
                "name": "Random Forest Regressor (Core Model)",
                "mae": round(rf_mae, 2),
                "rmse": round(rf_rmse, 2),
                "r2": round(rf_r2, 4),
                "mape": round(rf_mape, 2),
                "n_estimators": 120,
                "min_samples_leaf": 3
            }
        },
        "mae_improvement_pct": round(mae_improvement, 2),
        "airline_breakdown": airline_metrics,
        "feature_importances": feature_imp[:10]
    }
    
    with open("data/model_metrics.json", "w") as f:
        json.dump(metrics_summary, f, indent=2)
    print("Saved comprehensive metrics to data/model_metrics.json")
    
    return metrics_summary

if __name__ == "__main__":
    train_and_evaluate()
