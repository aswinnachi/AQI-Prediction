# A PROJECT BASED EVALUATION REPORT

## DIVISION OF COMPUTER SCIENCE AND ENGINEERING
## SCHOOL OF COMPUTER SCIENCE AND TECHNOLOGY
### KARUNYA INSTITUTE OF TECHNOLOGY AND SCIENCES
*(Declared as Deemed-to-be-University under Sec.3 of the UGC Act, 1956)*  
**A CHRISTIAN MINORITY RESIDENTIAL INSTITUTION**  
**AICTE Approved & NAAC Accredited**  
**Karunya Nagar, Coimbatore - 641 114, Tamil Nadu, India**

---

### COURSE CODE: 23CS2024
### COURSE NAME: DATA SCIENCE ECOSYSTEM
### SEMESTER: ODD SEMESTER 2026-2027 (III B.TECH / V SEMESTER)

---

## TITLE:
# TAMIL NADU AIR QUALITY INDEX (NAQI) FORECASTING AND GEOSPATIAL ASSESSMENT USING MACHINE LEARNING AND ATMOSPHERIC MODELING

### A REAL TIME PROJECT (PRODUCT) REPORT

**Submitted by:**
- **JOSHUA ISRAEL (URK24CS1034)**
- **BRITNY P (URK24CS1109)**
- **SANUSHA (UTK24CS1001)**

**Under the Guidance of:**
Faculty-in-Charge, Division of Computer Science and Engineering  
School of Computer Science and Technology  
Karunya Institute of Technology and Sciences

**OCTOBER 2026**

---

## ONLINE CERTIFICATION RECORD

**Student Name:** JOSHUA ISRAEL (URK24CS1034)  
**Certification Program:** Microsoft Certified: Azure Data Fundamentals / Data Science Ecosystem (DP-900)  
**Verification ID:** wE6v2-48Dm / Microsoft Certification Authority  
**Status:** Completed & Verified (Final Exam Attempted / Certified — 20 Marks Component)

---

## ABSTRACT

The project titled **“Tamil Nadu Air Quality Index (NAQI) Forecasting and Geospatial Assessment Using Machine Learning and Atmospheric Modeling”** investigates how atmospheric, meteorological, and chemical reanalysis data can be systematically ingested, processed, and evaluated to deliver accurate 72-hour air quality forecasts across all 38 revenue districts of Tamil Nadu, India. Rapid urbanization, vehicular traffic corridors, industrial zones (such as Ennore, Ranipet, and Tiruppur), and intensive agricultural biomass operations necessitate localized, reliable, and interpretable air quality intelligence.

The implementation builds a multi-tier data science ecosystem comprising an automated atmospheric data ingestion pipeline, an official Indian Central Pollution Control Board (CPCB) National Air Quality Index (NAQI) computational engine, machine learning regression models (calibrated XGBoost and Random Forest architectures), and an interactive multi-page Streamlit web dashboard. Real-time atmospheric predictors ($PM_{2.5}$, $PM_{10}$, $CO$, $NO_2$, $SO_2$, $O_3$, 2-meter temperature, relative humidity, atmospheric pressure, wind speed, wind direction, precipitation, and direct solar radiation) are retrieved using the Open-Meteo European Centre for Medium-Range Weather Forecasts (ECMWF) Copernicus Atmosphere Monitoring Service (CAMS) reanalysis feed.

A rigorous audit of the underlying data science pipeline revealed critical empirical and architectural insights:
1. **Target Leakage and Explanatory Mechanics:** Initial evaluation of the calibrated models yielded seemingly extraordinary performance metrics ($R^2 = 99.34\%$ with an RMSE of $3.24$ AQI points for XGBoost; $R^2 = 99.18\%$ with an RMSE of $3.60$ AQI points for Random Forest). However, a methodological audit demonstrates target leakage: the target $CPCB\_AQI$ is deterministically computed from the six primary criteria pollutants ($PM_{2.5}$, $PM_{10}$, $NO_2$, $SO_2$, $CO$, and $O_3$) via the MoEFCC piece-wise linear interpolation formula. Because these exact pollutant concentrations are provided as input features, the tree-based regressors function as high-precision piecewise linear approximators of the official CPCB sub-index maximization lookup function rather than discovering unobserved physical atmospheric dynamics.
2. **Data Provenance and Ground-Station Disparity:** The live and training feeds originate from modeled CAMS/ECMWF atmospheric grids ($0.25^\circ \times 0.25^\circ \approx 25\text{ km}$ spatial resolution) rather than physical Continuous Ambient Air Quality Monitoring Stations (CAAQMS) operated by the Tamil Nadu Pollution Control Board (TNPCB). Consequently, localized micro-hotspots (e.g., street canyons and industrial clusters) are smoothed into regional atmospheric averages.
3. **Network Resilience & Architectural Optimization:** When scaling the dashboard to all 38 districts, initial concurrent multi-threaded requests ($ThreadPoolExecutor$, 10 workers) induced local DNS daemon socket exhaustion ($[Errno\ 8]\ NameResolutionError$). This issue was systematically eliminated by refactoring the ingestion pipeline into a single multi-coordinate batch HTTP GET transaction ($latitude=lat_1,lat_2...$), resolving all 38 districts in approximately $0.7$ seconds while remaining resilient under cached Streamlit execution ($st.cache\_data$, TTL 900 seconds).
4. **Category Synchronization Bug Resolution:** The user interface previously computed highlight category labels from isolated pollutant sub-indices rather than mapping the predicted scalar AQI score through the official six-tier NAQI standard (Good: 0–50, Satisfactory: 51–100, Moderate: 101–200, Poor: 201–300, Very Poor: 301–400, Severe: 401–500). Implementing an authoritative categorization engine resolved this discrepancy, ensuring mathematical consistency across metric cards, time-series visualizations, and district leaderboards.

The resulting software artifact provides public health advisories, diurnal trend analysis, comparative multi-district trajectories, and geospatial Choropleth visualizers. This report details the full engineering and data science lifecycle, empirical validations, diagnostic audits, and documented project limitations.

---

# CHAPTER 1: INTRODUCTION

## 1.1 Background
Air pollution has emerged as one of the most pressing public health and environmental challenges in developing economies. In India, rapid industrial growth, increasing vehicular density, thermal power generation, construction dust, and seasonal agricultural biomass burning contribute significantly to elevated ambient concentrations of particulate matter ($PM_{2.5}$, $PM_{10}$) and hazardous gaseous precursors (Nitrogen Dioxide, Sulphur Dioxide, Carbon Monoxide, and Ground-level Ozone). Exposure to elevated atmospheric pollution has been causally linked to acute respiratory infections, chronic obstructive pulmonary disease (COPD), ischemic heart disease, and premature mortality.

To convey complex air quality information in an intuitive manner to the general public, the Ministry of Environment, Forest and Climate Change (MoEFCC), Government of India, along with the Central Pollution Control Board (CPCB), established the National Air Quality Index (NAQI) in October 2014. The NAQI translates multi-pollutant atmospheric chemical concentrations into a unified, dimensionless numeric scale ranging from 0 to 500, segmented into six descriptive health-risk categories: *Good*, *Satisfactory*, *Moderate*, *Poor*, *Very Poor*, and *Severe*.

Tamil Nadu, located in the southern peninsula of India, presents a unique atmospheric environment. Comprising 38 administrative districts spanning coastal plains, the Kaveri river basin, semi-arid interior tracts, and the Western Ghats mountain range, the state exhibits substantial intra-regional heterogeneity in emission profiles. Industrial centers such as Chennai (Manali, Ennore industrial corridors), Tiruppur (textile processing and dyeing boilers), Salem (iron and steel manufacturing), and Ranipet (tanneries and chemical manufacturing) contrast sharply with pristine ecological reserves such as the Nilgiris (Ooty) and Kodaikanal. Developing an intelligent, data-driven system capable of predicting localized AQI trajectories 72 hours in advance is essential for empowering citizens, vulnerable populations, municipal authorities, and environmental regulators to implement proactive mitigation strategies.

## 1.2 Problem Statement
While statutory Continuous Ambient Air Quality Monitoring Stations (CAAQMS) provide high-precision localized observations, their spatial distribution across Tamil Nadu is heavily concentrated in major metropolitan centers such as Chennai, Coimbatore, and Madurai. Over 25 of the 38 districts possess limited or no continuous real-time physical monitoring infrastructure, creating substantial observational blind spots across rural, agricultural, and semi-urban belts.

Furthermore, traditional physical air quality stations report retrospective measurements (what occurred over the preceding hour or 24 hours), offering no forward predictive capability. Previous modeling approaches deployed in academic and open-source prototypes suffered from four critical technical deficiencies:
1. **Regional Inappropriateness:** Models were frequently trained on foreign datasets (e.g., Karachi, Pakistan or US EPA baselines) utilizing foreign air quality standards that misclassify Indian pollution severity.
2. **Computational Inefficiency and Network Fragility:** Previous multi-district data scrapers launched unthrottled concurrent HTTP threads, triggering domain name resolution failures ($NameResolutionError$), socket exhaustion, and system crashes when querying multi-location APIs.
3. **Semantic Inconsistency:** Visual dashboards suffered from logical decoupling between numeric model predictions and categorical health advisories, resulting in erroneous outputs (e.g., classifying a severe AQI of 281 as "Satisfactory").
4. **Lack of Transparent Methodological Scrutiny:** Many predictive systems claim exceptional accuracy ($R^2 > 99\%$) without disclosing that the target index was deterministically calculated from the very same criteria pollutants provided as input features (target leakage).

The core objective of this project is to resolve these foundational challenges by building a robust, architecturally sound, and mathematically rigorous 72-hour CPCB NAQI prediction and geospatial visualization ecosystem for all 38 districts of Tamil Nadu.

## 1.3 Objectives
The primary objectives of this study are:
- **Comprehensive Geospatial Cataloging:** Formulate a structured geographical, demographic, and emission profile catalog for all 38 administrative districts of Tamil Nadu, incorporating precise geographic centroids, administrative regional classifications, and known industrial emission drivers.
- **Atmospheric Pipeline Engineering:** Construct an automated, fault-tolerant ingestion pipeline interfacing with the Open-Meteo and Copernicus Atmosphere Monitoring Service (CAMS) reanalysis feeds to capture 24-hour historical observations and 72-hour forward hourly atmospheric forecasts.
- **Standardized CPCB NAQI Engine Development:** Implement the official Central Pollution Control Board (CPCB) piece-wise linear interpolation algorithms, sub-index calculators, and color-coded health advisory matrices according to Indian environmental regulatory mandates.
- **Machine Learning Architecture & Benchmarking:** Train, calibrate, and compare supervised regression models (Random Forest Regressor and eXtreme Gradient Boosting / XGBoost Regressor) on regional atmospheric datasets, rigorously evaluating performance under both random and chronological holdout splits.
- **Target Leakage and Methodological Audit:** Conduct an in-depth empirical audit of feature-target relationships to determine the extent of target leakage, explanatory mechanics, and physical limitations inherent in predicting mathematical indices.
- **High-Performance Streamlit Web Application:** Deploy a responsive, multi-tabbed web dashboard incorporating interactive time-series plots, multi-district comparative trajectories, real-time provincial leaderboard rankings, and interactive Plotly geospatial maps.
- **Network Resilience Optimization:** Refactor legacy multi-threaded network queries into high-efficiency batch API transactions, implementing intelligent caching and calibrated fallback baselines to ensure continuous 100% operational uptime.

## 1.4 Scope and Significance
The scope of this project encompasses all 38 districts of Tamil Nadu, covering 13 meteorological and chemical variables across 72 forward hourly forecast steps. The engineering deliverables comprise the complete data collection scripts, model training pipelines, pickled model and scaler artifacts, the CPCB NAQI computational engine, and the interactive Streamlit user interface.

The significance of this work lies in its transparent, evidence-based approach to environmental data science:
- **Public Health Empowerment:** Provides sensitive populations (asthma sufferers, pediatric cohorts, elderly demographics) with clear, color-coded health warnings up to 3 days in advance.
- **Academic and Methodological Integrity:** Rather than masking high performance metrics behind opaque claims, this report transparently documents target leakage, reanalysis limitations, and the distinction between statistical curve fitting and physical atmospheric transport modeling.
- **Open Environmental Infrastructure:** Demonstrates how free-tier open atmospheric reanalysis feeds can be leveraged to democratize environmental monitoring in regions lacking multi-crore CAAQMS physical monitoring networks.

---

# CHAPTER 2: LITERATURE REVIEW

## 2.1 Environmental Monitoring & CPCB NAQI Standards
The assessment of ambient air quality in India is governed by the National Ambient Air Quality Standards (NAAQS) notified by the Central Pollution Control Board under the Air (Prevention and Control of Pollution) Act, 1981. The official National Air Quality Index (NAQI) system, developed by an expert technical group comprising environmental scientists, medical experts, and the Indian Institute of Technology (IIT) Kanpur, transformed air quality communication in India.

The CPCB NAQI considers eight primary pollutants: Particulate Matter with aerodynamic diameter $<2.5\ \mu\text{m}$ ($PM_{2.5}$), Particulate Matter $<10\ \mu\text{m}$ ($PM_{10}$), Nitrogen Dioxide ($NO_2$), Sulphur Dioxide ($SO_2$), Carbon Monoxide ($CO$), Ozone ($O_3$), Ammonia ($NH_3$), and Lead ($Pb$). Each pollutant possesses specific concentration breakpoints and averaging intervals (24-hour for $PM$, $NO_2$, $SO_2$, $NH_3$, and $Pb$; 8-hour for $CO$ and $O_3$). The overall AQI is governed by the *maximum operator principle*, defined as the highest sub-index among all evaluated pollutants ($I = \max(I_1, I_2, \dots, I_n)$), with the corresponding pollutant designated as the *prominent pollutant*.

Prior literature highlights that international air quality indices (such as the United States Environmental Protection Agency US-AQI or the European Air Quality Index) cannot be directly mapped to Indian atmospheric conditions. Indian baseline particulate matter levels are significantly higher due to arid crustal dust, tropical monsoon cycles, and high population density; applying foreign indices leads to chronic category distortion and public confusion.

## 2.2 Atmospheric Chemical Modeling vs Ground Monitoring
Traditional ambient air quality monitoring relies on ground-based Continuous Ambient Air Quality Monitoring Stations (CAAQMS). CAAQMS instruments utilize beta-attenuation monitors (BAM) for particulate matter, chemiluminescence analyzers for $NO_x$, ultraviolet fluorescence for $SO_2$, non-dispersive infrared (NDIR) spectroscopy for $CO$, and ultraviolet photometry for $O_3$. While highly accurate, CAAQMS infrastructure entails significant capital expenditure ($\approx ₹1.5\text{ to }₹2.0\text{ crore}$ per station) and intensive recurring maintenance, severely limiting rural and district-wide deployment.

In contrast, numerical weather prediction and global atmospheric reanalysis models—such as the Copernicus Atmosphere Monitoring Service (CAMS) integrated into the ECMWF Integrated Forecasting System (IFS)—provide globally gridded, continuous atmospheric chemical data. CAMS assimilates satellite retrievals (including MODIS AOD, Sentinel-5P TROPOMI trace gases) with emission inventories to project multi-layer pollutant transport at $0.25^\circ \times 0.25^\circ$ spatial resolution. Modern environmental informatics increasingly utilizes CAMS reanalysis feeds to bridge geographic data deserts where ground instrumentation is economically unfeasible.

## 2.3 Machine Learning Regression in Environmental Science
Statistical and machine learning approaches for air quality prediction have evolved rapidly over the past two decades. Early studies utilized Multiple Linear Regression (MLR) and classical Autoregressive Integrated Moving Average (ARIMA) models. While computationally efficient, linear approaches struggle to capture non-linear photochemical interactions (such as the secondary formation of tropospheric ozone from $NO_x$ and volatile organic compounds under intense solar radiation) and boundary-layer meteorological dynamics.

Supervised machine learning algorithms—specifically tree ensemble techniques such as Random Forests (Breiman, 2001) and Gradient Boosting Machines (Friedman, 2001; Chen & Guestrin, 2016)—have demonstrated superior predictive capacity in atmospheric benchmarks. Tree ensembles naturally accommodate complex feature interactions, non-linear thresholds, and multi-collinear meteorological predictors (temperature, humidity, wind vectors, and planetary boundary layer height).

## 2.4 Model Evaluation Metrics in Air Quality Informatics
Evaluating regression models in environmental data science requires balanced, multi-dimensional error metrics. Relying solely on the coefficient of determination ($R^2$) can be highly misleading when features share mathematical relationships with the target variable. Standard evaluation metrics include:
- **Mean Absolute Error (MAE):** Represents the average magnitude of absolute errors in original units ($AQI\ points$), providing a robust measure that does not disproportionately penalize outliers.
- **Root Mean Squared Error (RMSE):** Measures the standard deviation of residuals, heavily penalizing large prediction discrepancies. RMSE is sensitive to extreme pollution episodes.
- **Coefficient of Determination ($R^2$):** Measures the proportion of variance in the target variable explained by the model relative to a mean baseline.
- **Weighted Absolute Percentage Error (WAPE):** Normalizes the total absolute error by the aggregate ground truth, avoiding division-by-zero anomalies common in Mean Absolute Percentage Error (MAPE) during low pollution readings.

## 2.5 Explainability and Public Health Actionability
A predictive model in healthcare or environmental informatics is functionally inadequate if it operates solely as an uninterpretable "black box." In air quality management, end-users require insight into *why* a particular pollution spike is anticipated. If elevated AQI is driven by fine particulate matter ($PM_{2.5}$) during nocturnal hours, the actionable guidance centers on industrial fuel burning or boundary-layer temperature inversion. Conversely, if high AQI is driven by midday photochemical ozone ($O_3$), the guidance involves limiting outdoor exertion during peak solar irradiance.

Techniques such as TreeSHAP (Lundberg & Lee, 2017) and Gini feature importance matrices provide quantitative mechanisms to dissect feature contributions, ensuring that machine learning outputs translate directly into scientifically grounded health advisories.

## 2.6 Summary of Literature Review
The existing body of research demonstrates that:
1. Air quality modeling must strictly adhere to regional statutory definitions (CPCB NAQI for India).
2. Gridded reanalysis data serves as a vital proxy for unmonitored districts, provided spatial resolution limits are respected.
3. Ensemble machine learning models (XGBoost, Random Forest) offer the optimal balance of performance and interpretability.
4. Methodological rigor requires auditing for target leakage and ensuring seamless end-to-end synchronization between predicted numbers and categorical public health advisories.

---

# CHAPTER 3: SYSTEM DESIGN

## 3.1 System Architecture
The system follows a modular, decoupled data science architecture designed for fault tolerance, high computational throughput, and sub-second user responsiveness. The architecture comprises five distinct functional tiers:
1. **Atmospheric Data Ingestion Tier:** Interfaces with external atmospheric reanalysis APIs via HTTP sessions with automatic retry adapters.
2. **CPCB NAQI Computational Core:** Implements pure, deterministic sub-index mathematical formulations and category breakpoint mapping.
3. **Machine Learning Inference Engine:** Loads pre-trained ensemble models and scalers, executing vectorized 72-hour forward predictions.
4. **Resilience & Caching Layer:** Manages in-memory caching ($st.cache\_data$) with a 900-second Time-To-Live (TTL) and calibrated baseline fallbacks.
5. **Interactive Presentation Tier:** Streamlit web interface delivering multi-district comparisons, interactive time-series plots, geospatial choropleths, and CSV exports.

```
+-------------------------------------------------------------------------+
|                         SYSTEM ARCHITECTURE                             |
+-------------------------------------------------------------------------+
                                     |
   +---------------------------------+---------------------------------+
   |                                                                   |
   v                                                                   v
[Open-Meteo CAMS Air Quality API]                      [Open-Meteo Weather API]
(Hourly PM2.5, PM10, CO, NO2, SO2, O3)                 (Temp, Humidity, Pressure, Wind)
   |                                                                   |
   +---------------------------------+---------------------------------+
                                     |
                                     v
                 [Single Batch Multi-Coordinate Ingestion Tier]
                     (Requests Session + Exponential Backoff)
                                     |
                                     v
                    [Streamlit In-Memory Cache (TTL = 900s)]
                   (Fallback: Calibrated Regional Baselines)
                                     |
        +----------------------------+----------------------------+
        |                                                         |
        v                                                         v
[CPCB NAQI Math Engine]                                  [ML Inference Engine]
- Piecewise Sub-indices (PM2.5, PM10, etc.)             - Standard Scaler (scaler_tn.pkl)
- Overall AQI = max(Sub-indices)                         - XGBoost Regressor (xgboost_tn_aqi.pkl)
- Prominent Pollutant Identification                     - Random Forest Regressor (rf_tn_aqi.pkl)
- get_cpcb_category_from_aqi()                           - Vectorized 72h AQI Trajectory Output
        |                                                         |
        +----------------------------+----------------------------+
                                     |
                                     v
                       [Synchronized Presentation Tier]
               - Tab 1: 72-Hour Single District Forecast & Environmental Plots
               - Tab 2: Statewide 38-District Choropleth Map & Live Leaderboard
               - Tab 3: Multi-District Trajectory Comparison Tool
               - Tab 4: Industrial Profiles, Emission Sources & CPCB Health Guide
```

## 3.2 Atmospheric Data Processing Flow
The data processing sequence follows strict sequential steps to ensure high reliability:
1. **District Geocoding & Coordinate Extraction:** The user selects one of the 38 Tamil Nadu districts from the sidebar. Coordinates ($lat, lon$) and regional metadata are loaded from `config/tamil_nadu_districts.py`.
2. **Historical & Forecast Batch Fetching:** In `fetch_district_atmospheric_bundle()`, the system queries Open-Meteo for past 24 hours (measured/reanalyzed history) and forward 96 hours (forecast), slicing the forward sequence to precisely 72 hours.
3. **Harmonization & Imputation:** Chemical and meteorological streams are merged on UTC timestamp, converted to Indian Standard Time (IST, UTC+5:30), and missing values are imputed with regional baseline constants.
4. **Feature Vector Assembly & Standardization:** Features are structured to match the 15-variable feature signature:
   $$\mathbf{x} = [PM_{2.5}, PM_{10}, CO, NO_2, SO_2, O_3, T, RH, P, W_{spd}, W_{dir}, Rain, Solar, Hour, Month]$$
   The input vector is standardized via `scaler_tn.pkl`:
   $$\mathbf{z} = \frac{\mathbf{x} - \boldsymbol{\mu}}{\boldsymbol{\sigma}}$$
5. **Ensemble Model Inference:** The selected model (XGBoost or Random Forest) computes the continuous predicted AQI:
   $$\widehat{AQI} = f(\mathbf{z})$$
   Predictions are bounded to the valid statutory interval:
   $$\widehat{AQI}_{clipped} = \min(500, \max(1, \text{round}(\widehat{AQI})))$$
6. **Synchronized Categorization:** Each forecasted hourly point is evaluated via `get_cpcb_category_from_aqi()`, ensuring that category names, color hex codes, and badge emojis match the scalar value.
7. **Statewide Batch Snapshot:** Tab 2 triggers `fetch_all_districts_cpcb_snapshot()`, which passes all 38 coordinate pairs in a single comma-separated request to generate live state-wide rankings.

## 3.3 Dataset and Output Organisation
The codebase is structured into clear functional directories to maintain separation of concerns:
```
AQI-Prediction-main/
├── app.py                            # Streamlit web application & UI logic
├── requirements.txt                  # Python runtime dependencies
├── backup/
│   ├── tamil_nadu_atmospheric_data.csv # 1,080-row training dataset (5 TN districts)
│   ├── data_v1.csv ... datav5.csv    # Legacy project data files
├── config/
│   ├── cpcb_aqi.py                   # Statutory NAQI formulas & category mapping
│   ├── tamil_nadu_districts.py       # 38 TN districts coordinates & profiles
│   └── utils.py                      # Database helpers & model loading utilities
├── data_collection/
│   ├── fetch_current_data.py         # Standalone ingestion & MongoDB logger
│   └── prepare_training_data.py      # Feature store export script
├── models/
│   ├── train_tamil_nadu_models.py    # Training script for XGBoost & Random Forest
│   └── saved_models/
│       ├── registry.json             # Model metadata, RMSE, R2, and feature lists
│       ├── xgboost_tn_aqi.pkl        # Serialized XGBoost Regressor
│       ├── rf_tn_aqi.pkl             # Serialized Random Forest Regressor
│       └── scaler_tn.pkl             # Serialized StandardScaler
└── reports/
    └── figures/                      # Generated evaluation and diagnostic plots
```

## 3.4 Feature Design and Target Leakage Analysis
A primary focus of system design is feature transparency. In environmental modeling, target leakage occurs when an input feature mathematically encapsulates the target variable.

In this system:
- Target Variable: $CPCB\_AQI = \max(I_{PM2.5}, I_{PM10}, I_{NO2}, I_{SO2}, I_{CO}, I_{O3})$
- Input Features: $PM_{2.5}, PM_{10}, CO, NO_2, SO_2, O_3$, alongside ambient meteorological variables.

Because the six criteria pollutants are provided directly to the model, the regressor does not need to learn complex atmospheric chemical transport. Instead, it learns a piecewise linear regression mapping the six chemical inputs to their maximum statutory sub-index. This explains why tree ensemble models achieve $>99\%$ $R^2$ on holdout datasets.

In operational deployment, this design is utilized intentionally: the Open-Meteo API outputs future hourly chemical concentrations modeled by ECMWF CAMS. The machine learning model acts as a high-speed inference surrogate, mapping forecasted pollutant vectors into the Indian CPCB standard while accounting for local meteorological scaling.

## 3.5 38-District Geospatial and Batch Design
Querying 38 individual district coordinates via separate HTTP requests introduces substantial network overhead, potential socket drops, and rate-limiting penalties. Open-Meteo supports multi-location batching through comma-separated coordinate strings:
$$\text{latitude} = lat_1, lat_2, \dots, lat_{38} \quad \text{and} \quad \text{longitude} = lon_1, lon_2, \dots, lon_{38}$$

When invoked with multiple coordinate pairs, the API returns a JSON array of 38 objects, matching the exact order of the input query. This reduces network round-trip overhead from 38 sequential connections ($\approx 12\text{ to }18\text{ seconds}$) down to a single HTTP transaction completed in $\approx 0.7\text{ seconds}$.

---

# CHAPTER 4: IMPLEMENTATION

## 4.1 Development Environment
The implementation was developed and tested within the following software and hardware environment:
- **Operating System:** macOS Darwin (Unix-based, Apple Silicon architecture)
- **Programming Language:** Python 3.11.14
- **Core Libraries:**
  - `streamlit` (v1.40+): Web user interface and state management
  - `scikit-learn` (v1.3.0+): Preprocessing, evaluation metrics, and Random Forest modeling
  - `xgboost` (v2.0.0+): Gradient boosted decision trees
  - `pandas` (v2.1.0+) & `numpy` (v1.24.0+): Numerical data structures and vectorized array operations
  - `plotly` (v5.17.0+): Interactive data visualization and geospatial map rendering
  - `requests` (v2.31.0+): HTTP client with custom retry adapters

## 4.2 Data Ingestion & Atmospheric Feeds
Data ingestion is implemented in `fetch_district_atmospheric_bundle()` and `fetch_all_districts_cpcb_snapshot()`. To ensure resilience against intermittent network timeouts, a specialized `requests.Session` is mounted with an HTTP adapter utilizing exponential backoff:
$$\text{Backoff Factor} = 0.3, \quad \text{Status Force List} = [500, 502, 503, 504], \quad \text{Total Retries} = 3$$

The API queries the Open-Meteo Air Quality endpoint:
`https://air-quality-api.open-meteo.com/v1/air-quality`  
requesting hourly chemical constituents ($PM_{2.5}, PM_{10}, CO, NO_2, SO_2, O_3$), simultaneously querying the weather endpoint:
`https://api.open-meteo.com/v1/forecast`  
for meteorological covariates (temperature, relative humidity, surface pressure, wind speed at 10m, wind direction at 10m, precipitation, and solar radiation).

## 4.3 Feature Selection and Preprocessing
The model ingestion pipeline requires 15 continuous features:
$$\mathcal{F} = \{PM_{2.5}, PM_{10}, CO, NO_2, SO_2, O_3, T, RH, P, W_{spd}, W_{dir}, Rain, Solar, Hour, Month\}$$

Because pollutants exhibit disparate numerical scales (e.g., $CO$ concentrations frequently exceed $200\ \mu\text{g/m}^3$, while $SO_2$ typically ranges between $2\text{ and }25\ \mu\text{g/m}^3$), all features are standardized using `StandardScaler`:
$$z_j = \frac{x_j - \mu_j}{\sigma_j}$$
The scaler is fitted strictly on training data and serialized as `models/saved_models/scaler_tn.pkl` to prevent data leakage during inference.

## 4.4 Machine Learning Model Training
The training workflow is implemented in `models/train_tamil_nadu_models.py`. Training data originates from `backup/tamil_nadu_atmospheric_data.csv`, containing 1,080 hourly records across five representative Tamil Nadu districts: Chennai (industrial/coastal), Coimbatore (western industrial), Madurai (southern urban), Salem (mining/steel belt), and Nilgiris (ecologically sensitive mountain highlands).

Two regression architectures were implemented and trained:
1. **XGBoost Regressor (`xgboost_tn_aqi.pkl`):**
   - Hyperparameters: `n_estimators=150`, `max_depth=5`, `learning_rate=0.08`, `subsample=0.8`, `colsample_bytree=0.8`, `random_state=42`.
   - Objective: `reg:squarederror`.
2. **Random Forest Regressor (`rf_tn_aqi.pkl`):**
   - Hyperparameters: `n_estimators=150`, `max_depth=12`, `random_state=42`, `n_jobs=-1`.
   - Criterion: Mean Squared Error (MSE).

Both trained models are registered in `models/saved_models/registry.json` alongside their serialized scaler, feature names, and computed validation metrics.

## 4.5 Central Pollution Control Board (CPCB) NAQI Engine
The CPCB NAQI calculation engine is implemented in `config/cpcb_aqi.py`. For each pollutant $p$, the sub-index $I_p$ is determined using the statutory linear interpolation formula:
$$I_p = I_{lo} + \left(\frac{I_{hi} - I_{lo}}{B_{hi} - B_{lo}}\right) \times (C_p - B_{lo})$$
where:
- $C_p$ is the observed concentration of pollutant $p$.
- $[B_{lo}, B_{hi}]$ is the breakpoint concentration interval enclosing $C_p$.
- $[I_{lo}, I_{hi}]$ is the corresponding sub-index score interval enclosing $I_p$.

The overall index is governed by:
$$AQI = \max_{p \in \mathcal{P}} I_p$$

The prominent pollutant is identified as:
$$P_{prominent} = \arg\max_{p \in \mathcal{P}} I_p$$

To prevent category mismatches, the authoritative categorization function `get_cpcb_category_from_aqi(aqi_val)` maps any numeric scalar $AQI \in [0, 500]$ into its exact CPCB designation:

| Category | AQI Range | Level | Official CPCB Color | Hex Code | Badge Emoji |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Good** | 0 – 50 | 1 | Dark Green | `#059669` | 🟢 |
| **Satisfactory** | 51 – 100 | 2 | Light Green | `#84cc16` | 🟡 |
| **Moderate** | 101 – 200 | 3 | Yellow / Amber | `#f59e0b` | 🟠 |
| **Poor** | 201 – 300 | 4 | Orange | `#f97316` | 🔴 |
| **Very Poor** | 301 – 400 | 5 | Red | `#dc2626` | 🟣 |
| **Severe** | 401 – 500 | 6 | Maroon / Crimson | `#7f1d1d` | 🟤 |

*(Note on emoji representation: Standard Unicode lacks distinct light green and maroon colored circle glyphs. The UI utilizes the closest available Unicode colored circles: `🟢`, `🟡`, `🟠`, `🔴`, `🟣`, `🟤`.)*

## 4.6 Streamlit Real-Time Dashboard Implementation
The front-end user experience is built in `app.py`, featuring an intuitive sidebar navigation structure and four dedicated analysis tabs:
- **Sidebar:** District selector (with Chennai prioritized at index 0), geographic metadata display, model selector (Auto-select Best, XGBoost, Random Forest), cache clearing button, and optional MongoDB Atlas credentials expander.
- **Tab 1: District 72h Forecast:** Displays current pollutant metrics, summary highlight cards (Peak AQI, Lowest AQI, Average AQI, Dominant Category), dynamic health advisory alert, interactive Plotly 72-hour AQI trajectory curve with CPCB color bands, environmental covariate multi-axis trends, feature importance horizontal bar chart, and hourly tabular forecast with CSV download capability.
- **Tab 2: Statewide Map & Leaderboard:** Statewide summary metrics (Cleanest district, Most polluted district, State average AQI, Count of districts in Good/Satisfactory), interactive Plotly Geo bubble map of Tamil Nadu centered at ($11.1271^\circ\text{N}, 78.6569^\circ\text{E}$), and sortable 38-district leaderboard table.
- **Tab 3: Multi-District Comparison:** Allows concurrent selection of 2 to 5 districts, plotting overlaid 72-hour forecast curves over standard CPCB warning zones alongside comparative summary tables.
- **Tab 4: Profiles & Environmental Guide:** Documents administrative identity, primary industrial emission contributors, official CPCB/TNPCB public health precaution guidelines, and Tamil Nadu clean air initiatives.

---

# CHAPTER 5: TESTING AND VALIDATION

## 5.1 Testing Approach
A comprehensive testing and verification protocol was executed to validate the computational, predictive, and architectural integrity of the system:
1. **Mathematical Verification:** Validated the sub-index interpolation formulas against published CPCB technical manual test cases.
2. **Empirical Model Validation:** Re-evaluated trained model artifacts under both random shuffle holdouts and chronological time-series holdouts.
3. **Network Fault Tolerance Testing:** Evaluated system behavior under simulated DNS resolution failures, API timeouts, and cold starts.
4. **End-to-End User Experience Auditing:** Verified district switching performance, category synchronization, and leaderboard accuracy across multiple districts via automated browser subagents.

## 5.2 Unit Testing and API Response Verification
Unit tests verified the response formats of the Open-Meteo API under both single-coordinate and multi-coordinate configurations:
- **Single-coordinate query:** Verified that passing a single latitude/longitude pair returns a single JSON dictionary object (`dict`).
- **Multi-coordinate query (Batching):** Verified that passing comma-separated coordinates returns a JSON list (`list`) containing exactly 38 dictionary elements matching the district sequence.
- **CPCB Categorization Test Suite:** Verified that boundary values evaluate correctly:
  - Input: $AQI = 46 \implies \text{Good (Level 1, Badge: 🟢)}$
  - Input: $AQI = 75 \implies \text{Satisfactory (Level 2, Badge: 🟡)}$
  - Input: $AQI = 105 \implies \text{Moderate (Level 3, Badge: 🟠)}$
  - Input: $AQI = 227 \implies \text{Poor (Level 4, Badge: 🔴)}$
  - Input: $AQI = 281 \implies \text{Poor (Level 4, Badge: 🔴)}$

## 5.3 Empirical Model Validation and Split Audit
To verify the claimed evaluation metrics, the validation suite was re-executed using `models/saved_models/xgboost_tn_aqi.pkl` and `models/saved_models/rf_tn_aqi.pkl`.

### Split Methodology Comparison:
1. **Random Holdout Split (80/20 Shuffle):**
   - The dataset of 1,080 rows was randomly partitioned using `train_test_split(test_size=0.2, random_state=42)`.
   - **XGBoost:** $R^2 = 0.993375\ (99.34\%)$, $\text{RMSE} = 3.2433\ AQI\ points$.
   - **Random Forest:** $R^2 = 0.991833\ (99.18\%)$, $\text{RMSE} = 3.6012\ AQI\ points$.
2. **Chronological Holdout Split (Time-Series Order):**
   - The dataset was ordered chronologically by timestamp. The initial 80% (first 864 hours) served as the training baseline, and the final 20% (last 216 hours) served as the unseen forward holdout.
   - **XGBoost:** $R^2 = 0.997750\ (99.78\%)$, $\text{RMSE} = 2.9573\ AQI\ points$.
   - **Random Forest:** $R^2 = 0.996285\ (99.63\%)$, $\text{RMSE} = 3.7998\ AQI\ points$.

The empirical evaluation confirms that the reported metrics are mathematically reproducible and that the models do not degrade under chronological holdouts due to the continuous presence of dominant chemical features ($PM_{2.5}, O_3$).

## 5.4 Network Resilience and DNS Diagnostics
Testing the legacy multi-threaded implementation revealed the mechanism behind the observed failure:
- **Legacy Behavior:** In `fetch_all_districts_cpcb_snapshot()`, 38 separate threads were dispatched via `ThreadPoolExecutor(max_workers=10)`. When hitting external domain `air-quality-api.open-meteo.com`, macOS `mDNSResponder` dropped socket requests under rapid concurrent bursts, throwing `NameResolutionError: [Errno 8] nodename nor servname provided, or not known`.
- **Refactored Batch Behavior:** The single-request batch architecture makes exactly 1 HTTP call. In live testing, all 38 districts loaded consistently in $0.68\text{ seconds}$ without a single DNS drop.
- **Network Disconnection Simulation:** When network connectivity was artificially disabled, the system gracefully caught the exception, logged a structured notice to the console, and seamlessly engaged the calibrated regional diurnal baseline fallback, preventing Streamlit runtime crashes.

## 5.5 Validation Outcome
The testing cycle confirms that:
1. The CPCB NAQI calculation engine conforms strictly to Indian statutory standards.
2. The reported $R^2$ ($99.34\%$) and RMSE ($3.24$) are empirically accurate under the defined feature space.
3. Network fragility has been eliminated through batching.
4. Scalar AQI predictions and categorical advisories are 100% synchronized across all user interfaces.

---

# CHAPTER 6: RESULTS AND DISCUSSION

## 6.1 Model Performance and Benchmark Results
The empirical evaluation demonstrates that both ensemble architectures achieve exceptional precision in learning the statutory CPCB transformation mapping:

| Model Architecture | Split Type | $R^2$ Score | RMSE ($AQI\ pts$) | MAE ($AQI\ pts$) | Training Time |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **XGBoost Regressor** | Random Holdout (80/20) | **0.9934** | **3.24** | **1.82** | $\approx 0.42\text{ s}$ |
| **Random Forest Regressor** | Random Holdout (80/20) | 0.9918 | 3.60 | 2.14 | $\approx 1.85\text{ s}$ |
| **XGBoost Regressor** | Chronological (Last 20%) | **0.9978** | **2.96** | **1.65** | $\approx 0.42\text{ s}$ |
| **Random Forest Regressor** | Chronological (Last 20%) | 0.9963 | 3.80 | 2.28 | $\approx 1.85\text{ s}$ |

XGBoost marginally outperforms Random Forest across both split methods, exhibiting tighter residual distributions and lower computational latency during inference.

## 6.2 Target Leakage and Diagnostic Interpretation
Figure 6.1 and Figure 6.2 (generated in `reports/figures/`) illustrate the diagnostic dynamics of the models:
- **Actual vs. Predicted Diagnostics:** The scatter plots for both XGBoost and Random Forest lie almost perfectly along the $45^\circ$ dashed identity line ($y = x$). Residuals are tightly bounded within $\pm 6\ AQI\ points$ across the entire operating range ($AQI \in [20, 220]$).
- **Feature Importance Analysis:** Gini impurity and gain metrics indicate that Ground-level Ozone ($O_3$) accounts for approximately $43.1\%$ of model importance in XGBoost and $>95\%$ in Random Forest, followed by Relative Humidity ($28.7\%$), $PM_{10}$ ($8.7\%$), and $PM_{2.5}$ ($8.1\%$).

### Methodological Interpretation:
The dominance of $O_3$ and $PM_{2.5}$ reflects the mathematical reality of the CPCB breakpoint table in the Tamil Nadu dataset. During sunny, high-temperature daytime hours in Tamil Nadu, photochemical ozone sub-indices frequently exceed particulate sub-indices, becoming the governing maximum sub-index ($I_{max}$). The model learns this switching behavior precisely. Evaluators must recognize that while the model exhibits $99.34\%$ $R^2$, it is functioning as an automated surrogate mapping function from forecasted atmospheric chemistry to the CPCB index, rather than predicting chemical concentrations from raw meteorology alone.

## 6.3 Geospatial and Multi-District Findings
Live execution of the 38-district batch snapshot revealed significant regional patterns across Tamil Nadu:
- **Northern Industrial Corridor (Chennai, Tiruvallur, Ranipet, Chengalpattu):** Exhibits elevated particulate concentrations ($PM_{2.5} > 60\ \mu\text{g/m}^3$), resulting in CPCB AQI values ranging between 180 and 245 (*Moderate* to *Poor*). Elevated readings are driven by thermal power generation, port logistics, petrochemical refining, and heavy vehicular corridors.
- **Western Industrial & Textile Belt (Coimbatore, Tiruppur, Erode, Salem):** Displays diurnal spikes in $PM_{10}$ and $NO_2$ associated with industrial boilers, textile processing, and steel smelting. Peak AQI values range between 110 and 160 (*Moderate*).
- **Kaveri Delta & Agricultural Zone (Thanjavur, Tiruvarur, Nagapattinam):** Air quality remains predominantly *Satisfactory* ($AQI \in [65, 95]$), with occasional particulate elevations during post-harvest biomass clearance.
- **Southern Peninsula & Western Ghats (Nilgiris, Tenkasi, Kanniyakumari):** Consistently records the cleanest air quality statewide ($AQI \in [25, 55]$, *Good* to *Satisfactory*), benefiting from high elevation, dense forest canopy cover, and oceanic dispersion.

## 6.4 Challenges Encountered & Systematic Resolutions

### Challenge 1: NameResolutionError and Socket Exhaustion
- **Symptom:** Selecting Sivaganga or other districts intermittently displayed:  
  `HTTPSConnectionPool: Max retries exceeded ... Failed to resolve 'air-quality-api.open-meteo.com' ([Errno 8] nodename nor servname provided, or not known)`.
- **Root Cause Analysis:** A 10-worker thread pool executing 38 parallel HTTPS connections saturated local DNS caching daemons.
- **Proven Resolution:** Replaced multi-threading with a single batch HTTP GET request querying all 38 coordinate pairs simultaneously. Execution time dropped from 15 seconds to 0.7 seconds, with zero dropped connections.

### Challenge 2: Category Mismatch Bug
- **Symptom:** UI displayed contradictory cards such as `Peak Forecast AQI: 281 | Max Level: Satisfactory`.
- **Root Cause Analysis:** The card evaluated `calculate_cpcb_aqi(pm25=row['pm2_5'])` rather than evaluating the model's predicted AQI score.
- **Proven Resolution:** Created `get_cpcb_category_from_aqi()`. All visual metrics, summary highlights, and advisory banners now map directly from the predicted scalar AQI, establishing complete semantic consistency.

### Challenge 3: Open-Meteo Quota and Multi-Location Accounting
- **Technical Nuance:** While batching reduces HTTP connection overhead to 1 request, Open-Meteo's API accounting treats each location in a comma-separated query as an individual call towards the free-tier quota (10,000 calls/day). Querying 38 districts in 1 batch consumes 38 quota calls.
- **Resolution:** Implemented Streamlit in-memory caching (`@st.cache_data(ttl=900)`). The batch snapshot is executed at most once every 15 minutes, capping daily API consumption at $\approx 3,648$ calls, well within the free-tier ceiling.

## 6.5 Current Status and Discussion
The Tamil Nadu AQI Predictor is fully operational, stable, and running locally at `http://localhost:8501`. The software reliably serves 72-hour forward predictions, interactive multi-district comparisons, and state-wide geospatial maps for all 38 districts without runtime errors or uncaught exceptions.

---

# CHAPTER 7: CONCLUSION AND FUTURE WORK

## 7.1 Conclusion
This project developed an end-to-end machine learning and geospatial intelligence platform for 72-hour Air Quality Index forecasting across all 38 administrative districts of Tamil Nadu, India. By integrating Open-Meteo / Copernicus Atmospheric Monitoring Service (CAMS) reanalysis feeds with the official Central Pollution Control Board (CPCB) National AQI regulatory standard, the system bridges the observational gap for over 25 districts lacking continuous ground instrumentation.

The investigation demonstrated the necessity of rigorous data science audits:
- Identified and documented target leakage inherent in predicting regulatory indices from constituent chemical features.
- Re-verified empirical model performance ($R^2 = 99.34\%$ for XGBoost, $99.18\%$ for Random Forest).
- Eliminated critical networking vulnerabilities through single-request multi-coordinate batching.
- Synchronized all visual metrics, category classifications, and public health advisories into an authoritative CPCB compliance engine.

The resulting web application serves as a practical, accessible environmental informatics tool for researchers, policymakers, and the general public.

## 7.2 System Limitations
An honest technical assessment requires acknowledging key system limitations:
1. **Modeled Reanalysis vs. Ground-Truth CAAQMS:** The system utilizes ECMWF CAMS gridded reanalysis models ($0.25^\circ \approx 25\text{ km}$ resolution). Reanalysis smooths hyper-local emission spikes (e.g., immediate roadside vehicular plumes or specific industrial stacks) into grid-cell averages.
2. **Instantaneous vs. 24-Hour Averaging:** The official CPCB statutory standard defines AQI based on 24-hour running averages for particulate matter and 8-hour averages for ozone/CO. The current real-time application evaluates instantaneous hourly forecasts against statutory breakpoints, which may overestimate short-term diurnal volatility compared to 24-hour smoothed regulatory reports.
3. **Synthetic Baseline Fallback:** When internet connectivity is completely unavailable, the system deploys synthesized diurnal sinusoidal baselines tailored to regional district characteristics. While scientifically calibrated, these represent simulated approximations rather than live measurements.
4. **Non-Commercial License Constraints:** The Open-Meteo free API tier is licensed strictly for non-commercial, academic, and research applications, requiring commercial licensing if deployed in enterprise municipal contexts.

## 7.3 Future Work
Subsequent iterations of the platform can incorporate:
- **Direct CAAQMS Sensor Ingestion:** Develop automated web scrapers interfacing with the CPCB *Central Control Room for Air Quality Monitoring* portal to ingest physical ground-truth station data across Chennai, Coimbatore, and Madurai.
- **Physics-Informed Hybrid Modeling:** Implement deep learning architectures (such as Long Short-Term Memory / LSTM networks or Temporal Fusion Transformers) trained to forecast future pollutant concentrations directly from raw meteorological inputs and satellite AOD data, eliminating target leakage.
- **High-Resolution Urban Dispersion Modeling:** Integrate Gaussian plume dispersion models (e.g., AERMOD) with local OpenStreetMap road traffic density vectors to achieve street-level ($\approx 100\text{ m}$) micro-scale pollution mapping.
- **Automated SMS & WhatsApp Alerts:** Integrate Twilio or government SMS gateways to deliver proactive health warnings to registered citizens when regional AQI is forecasted to exceed the *Poor* threshold ($>200$).

## 7.4 Final Statement
The project demonstrates that responsible environmental data science requires both architectural resilience and methodological transparency. Achieving high computational accuracy is meaningful only when grounded in statutory compliance, transparent feature engineering, and robust software implementation. The Tamil Nadu NAQI Predictor establishes a solid foundation for regional air quality forecasting and actionable public health protection.

---

# REFERENCES

1. Breiman, L. (2001). Random forests. *Machine Learning*, 45(1), 5–32. https://doi.org/10.1023/A:1010933404324
2. Central Pollution Control Board (CPCB). (2014). *National Air Quality Index: Technical Report*. Ministry of Environment, Forest and Climate Change, Government of India. https://cpcb.nic.in/air-quality-index
3. Central Pollution Control Board (CPCB). (2015). *Guidelines for the Calculation of Air Quality Index (AQI)*. Parivesh Bhawan, East Arjun Nagar, Delhi, India.
4. Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, 785–794. https://doi.org/10.1145/2939672.2939785
5. Copernicus Atmosphere Monitoring Service (CAMS). (2023). *Global atmospheric composition reanalysis and forecasting models*. European Centre for Medium-Range Weather Forecasts (ECMWF). https://atmosphere.copernicus.eu/
6. Friedman, J. H. (2001). Greedy function approximation: A gradient boosting machine. *The Annals of Statistics*, 29(5), 1189–1232. https://doi.org/10.1214/aos/1013203451
7. Guttikunda, S. K., Goel, R., & Pant, P. (2014). Nature of air pollution, emission sources, and management in the Indian cities. *Atmospheric Environment*, 95, 501–510. https://doi.org/10.1016/j.atmosenv.2014.07.006
8. James, G., Witten, D., Hastie, T., Tibshirani, R., & Taylor, J. (2023). *An Introduction to Statistical Learning: With Applications in Python*. Springer. https://doi.org/10.1007/978-3-031-38747-0
9. Kuhn, M., & Johnson, K. (2013). *Applied Predictive Modeling*. Springer. https://doi.org/10.1007/978-1-4614-6849-3
10. Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems (NeurIPS)*, 30, 4765–4774.
11. Open-Meteo Weather & Air Quality API. (2026). *Free access meteorological and atmospheric chemical forecasting API documentation*. https://open-meteo.com/en/docs/air-quality-api
12. Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research*, 12, 2825–2830.
13. Ribeiro, M. T., Singh, S., & Guestrin, C. (2016). "Why should I trust you?": Explaining the predictions of any classifier. *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, 1135–1144.
14. Tamil Nadu Pollution Control Board (TNPCB). (2024). *Annual Report on Ambient Air Quality Monitoring in Tamil Nadu*. Government of Tamil Nadu, Chennai.
15. World Health Organization (WHO). (2021). *WHO Global Air Quality Guidelines: Particulate matter ($PM_{2.5}$ and $PM_{10}$), ozone, nitrogen dioxide, sulfur dioxide and carbon monoxide*. World Health Organization.

---

# APPENDICES

## APPENDIX A: PROJECT FILES AND WORKSPACE STRUCTURE

The implementation files recorded in the project repository comprise:
- `app.py`: Complete Streamlit web application supporting single-district 72-hour forecasting, statewide geospatial bubble mapping, multi-district comparative trajectories, and emission profiles.
- `config/cpcb_aqi.py`: Pure mathematical implementation of Indian CPCB linear interpolation sub-index calculators, overall AQI determination, and `get_cpcb_category_from_aqi()` categorization.
- `config/tamil_nadu_districts.py`: Comprehensive metadata catalog containing geographic coordinates, administrative zones, and industrial profiles for all 38 districts of Tamil Nadu.
- `models/train_tamil_nadu_models.py`: Automated model training script fitting and evaluating XGBoost and Random Forest regressors on regional atmospheric data.
- `models/saved_models/registry.json`: JSON metadata registry storing active model specifications, features, accuracy, RMSE, and feature importance rankings.
- `backup/tamil_nadu_atmospheric_data.csv`: 1,080-row empirical training dataset capturing 9 days of hourly multi-parameter atmospheric variables across five representative Tamil Nadu districts.
- `reports/figures/actual_vs_predicted.png`: Evaluation diagnostic plot comparing ground-truth CPCB AQI against predictions for XGBoost and Random Forest.
- `reports/figures/feature_importance.png`: Relative feature importance horizontal bar chart detailing dominant atmospheric variables.

---

## APPENDIX B: RECORDED MODEL BENCHMARK METRICS & CPCB NAQI REFERENCE

### Model Benchmark Summary Table:
| Metric / Parameter | XGBoost Regressor | Random Forest Regressor |
| :--- | :---: | :---: |
| **Model Serialization File** | `xgboost_tn_aqi.pkl` | `rf_tn_aqi.pkl` |
| **Scaler Artifact** | `scaler_tn.pkl` | `scaler_tn.pkl` |
| **Random Holdout $R^2$ Score** | **0.9934 (99.34%)** | **0.9918 (99.18%)** |
| **Random Holdout RMSE** | **3.24 AQI points** | **3.60 AQI points** |
| **Chronological Holdout $R^2$ Score** | **0.9978 (99.78%)** | **0.9963 (99.63%)** |
| **Chronological Holdout RMSE** | **2.96 AQI points** | **3.80 AQI points** |
| **Number of Estimators** | 150 | 150 |
| **Max Tree Depth** | 5 | 12 |
| **Number of Features** | 15 | 15 |

### Official CPCB NAQI Breakpoint Concentration Matrix:
| Pollutant | Good (0–50) | Satisfactory (51–100) | Moderate (101–200) | Poor (201–300) | Very Poor (301–400) | Severe (401–500) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **$PM_{2.5}$ ($\mu\text{g/m}^3$)** | 0 – 30 | 30.1 – 60 | 60.1 – 90 | 90.1 – 120 | 120.1 – 250 | 250.1 – 500 |
| **$PM_{10}$ ($\mu\text{g/m}^3$)** | 0 – 50 | 50.1 – 100 | 100.1 – 250 | 250.1 – 350 | 350.1 – 430 | 430.1 – 600 |
| **$NO_2$ ($\mu\text{g/m}^3$)** | 0 – 40 | 40.1 – 80 | 80.1 – 180 | 180.1 – 280 | 280.1 – 400 | 400.1 – 600 |
| **$SO_2$ ($\mu\text{g/m}^3$)** | 0 – 40 | 40.1 – 80 | 80.1 – 380 | 380.1 – 800 | 800.1 – 1600 | 1600.1 – 2400 |
| **$CO$ ($\text{mg/m}^3$)** | 0 – 1.0 | 1.01 – 2.0 | 2.01 – 10.0 | 10.01 – 17.0 | 17.01 – 34.0 | 34.01 – 50.0 |
| **$O_3$ ($\mu\text{g/m}^3$)** | 0 – 50 | 50.1 – 100 | 100.1 – 168 | 168.1 – 208 | 208.1 – 748 | 748.1 – 1000 |

---

## APPENDIX C: VERIFICATION EVIDENCE & EMPIRICAL TEST MATRIX

### Empirical Verification Test Results:
| Test ID | Test Description | Execution Method | Observed Outcome | Status |
| :---: | :--- | :--- | :--- | :---: |
| **TC-01** | Mathematical Interpolation Check | Sub-index verification ($PM_{2.5}=65.0$) | Yielded sub-index $117.3$ (*Moderate*) | **PASS** |
| **TC-02** | Category Mapping Engine | Evaluated inputs: 46, 75, 105, 227, 281 | Evaluated to Good, Satisfactory, Moderate, Poor, Poor | **PASS** |
| **TC-03** | Batch Ingestion Latency | Single HTTP call with 38 coordinate pairs | Completed in 0.68 seconds; 38 records parsed | **PASS** |
| **TC-04** | DNS Fault Tolerance | Executed query under simulated network drop | Clean console notice; fallback engaged smoothly | **PASS** |
| **TC-05** | Rapid District Switching | Cycled Chennai $\to$ Coimbatore $\to$ Sivaganga | UI updated in $<1.2\text{ s}$ per district without warnings | **PASS** |
| **TC-06** | Streamlit Server Latency | HTTP ping to `http://localhost:8501` | Server response latency: $0.006\text{ seconds}$ | **PASS** |

---

## APPENDIX D: CORRECTIONS TO EARLIER CLAIMS

In accordance with academic rigor and the independent review guidelines, the following table explicitly documents statements from preliminary summaries that were overstated, imprecise, or unverified, alongside their factual corrections:

| Preliminary Claim / Statement | Factual Audit Finding | Technical Correction & Clarification |
| :--- | :--- | :--- |
| *"Machine learning models predict future AQI with 99.34% accuracy."* | **Target Leakage:** The target variable $CPCB\_AQI$ was calculated directly from the criteria pollutants provided as model input features. | The model operates as an automated piecewise linear surrogate mapping function of the CPCB lookup formula. It does not predict atmospheric chemistry from weather physics alone. |
| *"Training was performed on real-time Tamil Nadu ground station observations."* | **Model Reanalysis Source:** Data in `backup/tamil_nadu_atmospheric_data.csv` originates from Open-Meteo / ECMWF CAMS reanalysis. | Training data represents gridded atmospheric chemical reanalysis ($25\text{ km}$ grid), not statutory Continuous Ambient Air Quality Monitoring Stations (CAAQMS) operated by TNPCB. |
| *"Sivaganga DNS failure was caused solely by remote server rate limiting."* | **Local DNS Socket Throttling:** 38 concurrent threads spawned by `ThreadPoolExecutor` overwhelmed the macOS `mDNSResponder` resolver. | The primary failure was local system socket resolution exhaustion under multi-threaded burst, resolved via single-transaction HTTP batching. |
| *"Batch querying reduces Open-Meteo daily API quota consumption to 1 call."* | **Multi-location Accounting:** Open-Meteo terms specify that each coordinate in a multi-location request counts as an individual call. | Querying 38 locations consumes 38 calls against the daily free limit (10,000 calls). Quota preservation is achieved via `st.cache_data` (TTL 900s), capping daily usage at $\approx 3,648$ calls. |
| *"Emoji circle badges represent official CPCB color standards."* | **Unicode Approximation:** CPCB uses dark green, light green, yellow, orange, red, and maroon. | Unicode circle emojis lack light green and maroon glyphs. The UI uses the closest Unicode sequence (`🟢`, `🟡`, `🟠`, `🔴`, `🟣`, `🟤`), while exact colors are preserved in Plotly charts via hex codes. |

---

## EVALUATION DETAILS SHEET

### SCHOOL OF COMPUTER SCIENCE AND TECHNOLOGY
### DIVISION OF COMPUTER SCIENCE AND ENGINEERING
**IA3 Evaluation Details (Odd Semester 2026-2027)**  
**Course Name:** Data Science Ecosystem  
**Course Code:** 23CS2024  
**Class / Semester:** III B.Tech / V Semester  
**Candidate Name:** JOSHUA ISRAEL  
**Register Number:** URK24CS1034  

### IA3 Continuous Assessment Rubric:
| Sl. No. | Assessment Component | Maximum Marks | Marks Awarded |
| :---: | :--- | :---: | :---: |
| **Certification Course (20 Marks)** | | | |
| 1 | Microsoft Certified: Azure Data Fundamentals (DP-900) / Data Science Ecosystem Exam Attempted / Certificate | 20 | |
| **Individual Project Development (20 Marks)** | | | |
| 2 | Evaluation of Problem Statement, Scope, and Atmospheric Dataset | 5 | |
| 3 | Methodology, CPCB NAQI Engine, Model Training & Result Analysis | 10 | |
| 4 | Technical Project Report Structure, Validation & Academic Integrity | 5 | |
| **TOTAL** | | **40** | |

<br><br>
**Signature of the Examiner:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Signature of the Faculty-in-Charge:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
