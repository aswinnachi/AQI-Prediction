"""
Train Machine Learning Models tailored specifically on Tamil Nadu Atmospheric Data
Targets both Indian CPCB National AQI (Continuous 0-500) and CPCB Category Level (1-6)
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

import pandas as pd
import numpy as np
import pickle
import json
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report
import xgboost as xgb

from config.cpcb_aqi import calculate_cpcb_aqi

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "backup" / "tamil_nadu_atmospheric_data.csv"
SAVED_MODELS_DIR = BASE_DIR / "models" / "saved_models"
SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("TRAINING MACHINE LEARNING MODELS ON REAL TAMIL NADU ATMOSPHERIC DATA")
print("=" * 80)

# Load data
df = pd.read_csv(DATA_FILE)
df['timestamp'] = pd.to_datetime(df['time'])
df['hour'] = df['timestamp'].dt.hour
df['month'] = df['timestamp'].dt.month

# Map column names to feature standard
df['pm2_5'] = df['pm2_5'].fillna(25.0)
df['pm10'] = df['pm10'].fillna(45.0)
df['co'] = df['carbon_monoxide'].fillna(200.0)
df['no2'] = df['nitrogen_dioxide'].fillna(15.0)
df['so2'] = df['sulphur_dioxide'].fillna(5.0)
df['o3'] = df['ozone'].fillna(60.0)
df['temp_c'] = df['temperature_2m'].fillna(28.0)
df['humidity_pct'] = df['relative_humidity_2m'].fillna(70.0)
df['pressure_hpa'] = df['surface_pressure'].fillna(1010.0)
df['wind_speed_kmh'] = df['wind_speed_10m'].fillna(10.0)
df['wind_dir_deg'] = df['wind_direction_10m'].fillna(180.0)
df['rain_mm'] = df['rain'].fillna(0.0)
df['solar_rad_wm2'] = df['direct_radiation'].fillna(0.0)

# Compute true CPCB AQI and level for each observation
cpcb_results = [
    calculate_cpcb_aqi(
        pm25=row['pm2_5'],
        pm10=row['pm10'],
        no2=row['no2'],
        so2=row['so2'],
        co=row['co'],
        o3=row['o3']
    )
    for _, row in df.iterrows()
]

df['cpcb_aqi'] = [r['aqi'] for r in cpcb_results]
df['cpcb_level'] = [r['level'] for r in cpcb_results]
df['cpcb_category'] = [r['category'] for r in cpcb_results]

feature_cols = [
    'pm2_5', 'pm10', 'co', 'no2', 'so2', 'o3',
    'temp_c', 'humidity_pct', 'pressure_hpa',
    'wind_speed_kmh', 'wind_dir_deg', 'rain_mm', 'solar_rad_wm2',
    'hour', 'month'
]

X = df[feature_cols]
y_aqi = df['cpcb_aqi']
y_cat = df['cpcb_level']

print(f"Dataset Shape: {X.shape}")
print("CPCB Category Distribution in Tamil Nadu dataset:")
print(df['cpcb_category'].value_counts())

# Split
X_train, X_test, y_aqi_train, y_aqi_test, y_cat_train, y_cat_test = train_test_split(
    X, y_aqi, y_cat, test_size=0.2, random_state=42
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# --- 1. Train XGBoost Regressor (Continuous CPCB AQI 0-500) ---
print("\n[1/3] Training XGBoost CPCB AQI Predictor...")
xgb_model = xgb.XGBRegressor(
    n_estimators=150,
    max_depth=5,
    learning_rate=0.08,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)
xgb_model.fit(X_train_scaled, y_aqi_train)
xgb_pred = xgb_model.predict(X_test_scaled)
xgb_r2 = r2_score(y_aqi_test, xgb_pred)
xgb_rmse = np.sqrt(mean_squared_error(y_aqi_test, xgb_pred))
print(f"   ✓ XGBoost R² Score: {xgb_r2:.4f} | RMSE: {xgb_rmse:.2f} AQI points")

# Feature Importance for XGBoost
fi_xgb = [
    {"feature": col, "importance": float(imp)}
    for col, imp in zip(feature_cols, xgb_model.feature_importances_)
]
fi_xgb.sort(key=lambda x: x['importance'], reverse=True)

# Save XGBoost
with open(SAVED_MODELS_DIR / "xgboost_tn_aqi.pkl", "wb") as f:
    pickle.dump(xgb_model, f)

# --- 2. Train Random Forest Regressor ---
print("\n[2/3] Training Random Forest CPCB AQI Predictor...")
rf_model = RandomForestRegressor(
    n_estimators=150,
    max_depth=12,
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train_scaled, y_aqi_train)
rf_pred = rf_model.predict(X_test_scaled)
rf_r2 = r2_score(y_aqi_test, rf_pred)
rf_rmse = np.sqrt(mean_squared_error(y_aqi_test, rf_pred))
print(f"   ✓ Random Forest R² Score: {rf_r2:.4f} | RMSE: {rf_rmse:.2f} AQI points")

fi_rf = [
    {"feature": col, "importance": float(imp)}
    for col, imp in zip(feature_cols, rf_model.feature_importances_)
]
fi_rf.sort(key=lambda x: x['importance'], reverse=True)

with open(SAVED_MODELS_DIR / "rf_tn_aqi.pkl", "wb") as f:
    pickle.dump(rf_model, f)

# Save common Scaler
with open(SAVED_MODELS_DIR / "scaler_tn.pkl", "wb") as f:
    pickle.dump(scaler, f)

# Update registry.json
registry_entries = [
    {
        "model_name": "Tamil Nadu XGBoost Predictor (CPCB NAQI)",
        "model_type": "xgboost",
        "version": "tn_xgb_v1",
        "accuracy": float(xgb_r2),
        "rmse": float(xgb_rmse),
        "model_file": "xgboost_tn_aqi.pkl",
        "scaler_file": "scaler_tn.pkl",
        "features": feature_cols,
        "feature_importance": fi_xgb,
        "forecast_hours": 72,
        "status": "active"
    },
    {
        "model_name": "Tamil Nadu Random Forest Predictor (CPCB NAQI)",
        "model_type": "random_forest",
        "version": "tn_rf_v1",
        "accuracy": float(rf_r2),
        "rmse": float(rf_rmse),
        "model_file": "rf_tn_aqi.pkl",
        "scaler_file": "scaler_tn.pkl",
        "features": feature_cols,
        "feature_importance": fi_rf,
        "forecast_hours": 72,
        "status": "active"
    }
]

with open(SAVED_MODELS_DIR / "registry.json", "w") as f:
    json.dump(registry_entries, f, indent=2)

print("\n" + "=" * 80)
print("TAMIL NADU MODELS SUCCESSFULLY TRAINED & REGISTERED!")
print(f"XGBoost R²: {xgb_r2:.2%} | Random Forest R²: {rf_r2:.2%}")
print("=" * 80)
