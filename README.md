# Tamil Nadu AQI Predictor (All 38 Districts)

A machine learning system that predicts Air Quality Index (AQI) 72 hours ahead for all **38 districts of Tamil Nadu, India** (including Chennai, Coimbatore, Madurai, Tiruchirappalli, Salem, Tiruppur, Nilgiris, and more). The project features real-time atmospheric data streaming, multi-model forecasting, state-wide geo mapping, and an interactive Streamlit dashboard.

## Overview

This project uses real-time weather and air pollution data from Open-Meteo and OpenWeather APIs to train and run classification models (XGBoost, Random Forest, SVM) that predict future AQI levels 3 days in advance.

## Features

- **All 38 Districts Covered**: Complete geographic coordinates and environmental profiles for every district in Tamil Nadu
- **72-Hour AQI Forecasting**: Predicts air quality 3 days in advance
- **State-wide Live Geo Map & Ranking**: Real-time comparative ranking from cleanest to most polluted districts
- **Multi-District Trajectory Comparison**: Compare 72-hour forecast trends for multiple districts side-by-side
- **Multiple ML Models**: XGBoost, Random Forest, and SVM classifiers
- **Automated Open-Meteo API Integration**: Fetches real-time atmospheric data without requiring paid keys
- **Feature Store & Model Registry**: Hybrid MongoDB Atlas cloud sync with resilient local offline fallback
- **Live Streamlit Dashboard**: Beautiful, multi-tab interactive web interface

## Data Sources

| Source | Data Provided |
|--------|---------------|
| [OpenWeather API](https://openweathermap.org/api) | Air pollution data (PM2.5, PM10, CO, NO₂, SO₂, O₃, AQI) |
| [Open-Meteo API](https://open-meteo.com/) | Weather data (temperature, humidity, pressure, wind, rain, solar radiation) |

## Model Features

The models are trained on 15 features:

**Pollutants**: PM2.5, PM10, CO, NO₂, SO₂, O₃  
**Weather**: Temperature, Humidity, Pressure, Wind Speed, Wind Direction, Rain, Solar Radiation  
**Temporal**: Hour, Month

## CPCB National Air Quality Index (NAQI) Categories

Calibrated to the official **Central Pollution Control Board (CPCB)** / Ministry of Environment, Forest and Climate Change (MoEFCC), Government of India:

| Level | Category | AQI Range | Color | Public Health Advisory |
| :---: | :--- | :---: | :---: | :--- |
| **1** | 🟢 **Good** | 0 – 50 | `#059669` | Minimal impact. Air quality is clean and healthy for all outdoor activities. |
| **2** | 🟡 **Satisfactory** | 51 – 100 | `#84cc16` | Minor breathing discomfort to sensitive individuals. Clean for the general public. |
| **3** | 🟠 **Moderate** | 101 – 200 | `#f59e0b` | Breathing discomfort to people with asthma, heart conditions, children and elderly. |
| **4** | 🔴 **Poor** | 201 – 300 | `#f97316` | Breathing discomfort to most people on prolonged outdoor exposure. |
| **5** | 🟣 **Very Poor** | 301 – 400 | `#dc2626` | Respiratory illness risk on prolonged exposure. Vulnerable groups stay indoors. |
| **6** | 🟤 **Severe** | 401 – 500 | `#7f1d1d` | Emergency condition. Affects healthy people and seriously impacts sensitive ailments. |

## Project Evaluation Report

A comprehensive technical and academic evaluation report is included in the repository:
- **PDF Report**: [`report.pdf`](report.pdf) (25 pages formatted for Karunya academic evaluation)
- **Markdown Report**: [`report.md`](report.md)

## Architecture

```
┌─────────────────┐     ┌─────────────────┐
│  OpenWeather    │     │   Open-Meteo    │
│      API        │     │      API        │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
         ┌───────────────────────┐
         │   GitHub Actions      │
         │  (Hourly Collection)  │
         └───────────┬───────────┘
                     ▼
         ┌───────────────────────┐
         │   MongoDB Atlas       │
         │   ┌───────────────┐   │
         │   │ Feature Store │   │
         │   └───────────────┘   │
         │   ┌───────────────┐   │
         │   │Model Registry │   │
         │   └───────────────┘   │
         └───────────┬───────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │   SVM   │ │ Random  │ │ XGBoost │
   │         │ │ Forest  │ │         │
   └─────────┘ └─────────┘ └─────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   Streamlit App       │
         │   (Live Dashboard)    │
         └───────────────────────┘
```

## GitHub Actions Workflows

### Hourly Data Collection
- **Schedule**: Every hour (`0 * * * *`)
- **Action**: Fetches current AQI and weather data, stores in MongoDB feature store
- **File**: `.github/workflows/fetch_data_hourly.yml`

### Daily Model Retraining
- **Schedule**: Daily at 2:00 AM UTC (`0 2 * * *`)
- **Action**: Retrains all three models and registers them in MongoDB
- **File**: `.github/workflows/retrain_models_daily.yml`

## Project Structure

```
AQI-Predictor/
├── app.py                          # Streamlit dashboard application
├── requirements.txt                # Python dependencies
├── config/
│   └── utils.py                    # Shared utilities (data loading, model registration)
├── data_collection/
│   ├── fetch_current_data.py       # Hourly data fetching script
│   └── prepare_training_data.py    # Training data preparation
├── models/
│   ├── train_randomforest.py       # Random Forest training script
│   ├── train_svm.py                # SVM training script
│   └── train_xgboost.py            # XGBoost training script
├── notebooks/
│   ├── aqi_eda.ipynb               # Exploratory data analysis
│   ├── shap_analysis.ipynb         # SHAP model interpretability analysis
│   ├── get_data.ipynb              # Data retrieval notebook
│   └── send_data.ipynb             # Data upload notebook
├── .github/workflows/
│   ├── fetch_data_hourly.yml       # Hourly data collection workflow
│   └── retrain_models_daily.yml    # Daily retraining workflow
└── backup/                         # Historical data backups
```

## Setup

### Prerequisites
- Python 3.12+
- MongoDB Atlas account
- OpenWeather API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/AQI-Predictor.git
   cd AQI-Predictor
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your credentials:
   ```env
   OPENWEATHER_API_KEY=your_openweather_api_key
   MONGODB_USERNAME=your_mongodb_username
   MONGODB_PASSWORD=your_mongodb_password
   MONGODB_CLUSTER=your_cluster.mongodb.net
   ```
4. Set up GitHub Actions secrets in your repository settings with the credentials from your `.env` file.

### Live Dashboard

The application is deployed and accessible here:  
https://aqi-prediction-y2pubhjmdctw4t3tiyenpj.streamlit.app/


### Running Locally

**Streamlit App:**
```bash
streamlit run app.py
```

**Manual Data Collection:**
```bash
python data_collection/fetch_current_data.py
```

**Train Models:**
```bash
python models/train_xgboost.py
python models/train_randomforest.py
python models/train_svm.py
```

## Environment Variables

For GitHub Actions, add these secrets to your repository:

| Secret | Description |
|--------|-------------|
| `OPENWEATHER_API_KEY` | API key from OpenWeather |
| `MONGODB_USERNAME` | MongoDB Atlas username |
| `MONGODB_PASSWORD` | MongoDB Atlas password |
| `MONGODB_CLUSTER` | MongoDB cluster URL |

## Tech Stack

- **ML/Data**: scikit-learn, XGBoost, pandas, NumPy
- **Interpretability**: SHAP (SHapley Additive exPlanations)
- **Database**: MongoDB Atlas
- **Frontend**: Streamlit, Plotly
- **Automation**: GitHub Actions
- **APIs**: OpenWeather, Open-Meteo

## SHAP Analysis

The project includes SHAP (SHapley Additive exPlanations) analysis for model interpretability. SHAP values help understand:

- **Global Feature Importance**: Which features have the most impact on predictions overall
- **Local Explanations**: How each feature contributes to individual predictions
- **Feature Interactions**: How features work together to influence AQI forecasts

### Running SHAP Analysis

```bash
jupyter notebook notebooks/shap_analysis.ipynb
```

The notebook generates:
- Summary plots (global feature importance)
- Beeswarm plots (SHAP value distributions)
- Waterfall plots (single prediction explanations)
- Dependence plots (feature interactions)

Results are saved to the `docs/` folder.
