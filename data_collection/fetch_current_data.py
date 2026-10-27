import requests
import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

# Add root directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.tamil_nadu_districts import TN_DISTRICTS, DEFAULT_DISTRICT

# Load environment variables
load_dotenv()

# Parse CLI arguments
parser = argparse.ArgumentParser(description="Fetch live AQI and weather data for Tamil Nadu districts")
parser.add_argument("--district", type=str, default=DEFAULT_DISTRICT, help="District name in Tamil Nadu")
args = parser.parse_args()

selected_district = args.district
if selected_district not in TN_DISTRICTS:
    print(f"Unknown district '{selected_district}'. Defaulting to {DEFAULT_DISTRICT}.")
    selected_district = DEFAULT_DISTRICT

district_meta = TN_DISTRICTS[selected_district]
LAT = district_meta["lat"]
LON = district_meta["lon"]

# Configuration
API_KEY = os.getenv("OPENWEATHER_API_KEY")
MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
MONGODB_CLUSTER = os.getenv("MONGODB_CLUSTER")

print("=" * 80)
print(f"FETCHING CURRENT AQI AND WEATHER DATA FOR {selected_district.upper()}, TAMIL NADU")
print(f"Coordinates: Lat {LAT}, Lon {LON} | Region: {district_meta['region']}")
print("=" * 80)

# Optional MongoDB connection
client = None
feature_store = None
if MONGODB_USERNAME and MONGODB_PASSWORD and MONGODB_CLUSTER:
    try:
        CONNECTION_STRING = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_CLUSTER}/"
        client = MongoClient(CONNECTION_STRING, serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        db = client["aqi_prediction"]
        feature_store = db["feature_store"]
        print("   ✓ Connected to MongoDB Atlas")
    except Exception as e:
        print(f"   [Notice] MongoDB Atlas not available: {e}")

try:
    pollution_data = None
    
    # 1. Try OpenWeather API if key is present
    if API_KEY and API_KEY != "your_openweather_api_key_here":
        try:
            print("\n[1/3] Fetching air pollution from OpenWeather API...")
            pollution_url = "http://api.openweathermap.org/data/2.5/air_pollution"
            p_params = {'lat': LAT, 'lon': LON, 'appid': API_KEY}
            p_res = requests.get(pollution_url, params=p_params, timeout=5).json()
            if 'list' in p_res and len(p_res['list']) > 0:
                p_item = p_res['list'][0]
                pollution_data = {
                    'dt': p_item['dt'],
                    'aqi': p_item['main']['aqi'],
                    'components': p_item['components']
                }
                print("   ✓ OpenWeather air pollution data fetched")
        except Exception as e:
            print(f"   [Notice] OpenWeather fetch failed: {e}")
            
    # Fallback to Open-Meteo Air Quality API
    if not pollution_data:
        print("\n[1/3] Fetching air pollution from Open-Meteo Air Quality API...")
        om_aq_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
        om_params = {
            'latitude': LAT,
            'longitude': LON,
            'hourly': 'pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,us_aqi',
            'past_days': 1,
            'forecast_days': 0,
            'timezone': 'Asia/Kolkata'
        }
        om_res = requests.get(om_aq_url, params=om_params, timeout=10).json()
        if 'hourly' in om_res:
            h = om_res['hourly']
            us_aqi_val = h.get('us_aqi', [50])[-1] or 50
            # Map US AQI to 1-5 scale
            if us_aqi_val <= 50:
                epa_level = 1
            elif us_aqi_val <= 100:
                epa_level = 2
            elif us_aqi_val <= 150:
                epa_level = 3
            elif us_aqi_val <= 200:
                epa_level = 4
            else:
                epa_level = 5
                
            pollution_data = {
                'dt': int(datetime.utcnow().timestamp()),
                'aqi': epa_level,
                'components': {
                    'pm2_5': h.get('pm2_5', [25.0])[-1] or 25.0,
                    'pm10': h.get('pm10', [45.0])[-1] or 45.0,
                    'co': h.get('carbon_monoxide', [200.0])[-1] or 200.0,
                    'no2': h.get('nitrogen_dioxide', [15.0])[-1] or 15.0,
                    'so2': h.get('sulphur_dioxide', [5.0])[-1] or 5.0,
                    'o3': h.get('ozone', [60.0])[-1] or 60.0,
                }
            }
            print("   ✓ Open-Meteo air pollution data fetched")

    # 2. Fetch current weather data from Open-Meteo
    print("\n[2/3] Fetching current weather data from Open-Meteo...")
    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_params = {
        'latitude': LAT,
        'longitude': LON,
        'current': 'temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,wind_direction_10m,rain,direct_radiation',
        'timezone': 'Asia/Kolkata'
    }
    w_res = requests.get(weather_url, params=weather_params, timeout=10).json()
    if 'current' not in w_res:
        print("   ✗ Failed to fetch weather data")
        exit(1)
        
    weather_data = w_res['current']
    print("   ✓ Weather data fetched")

    # 3. Combine and prepare record
    print("\n[3/3] Preparing data record...")
    ts = pollution_data['dt']
    dt_obj = datetime.fromtimestamp(ts)

    record = {
        "district": selected_district,
        "region": district_meta["region"],
        "timestamp": ts,
        "year": dt_obj.year,
        "month": dt_obj.month,
        "day": dt_obj.day,
        "hour": dt_obj.hour,
        "epa_aqi": pollution_data['aqi'],
        "pm2_5": pollution_data['components']['pm2_5'],
        "pm10": pollution_data['components']['pm10'],
        "co": pollution_data['components']['co'],
        "no2": pollution_data['components']['no2'],
        "so2": pollution_data['components']['so2'],
        "o3": pollution_data['components']['o3'],
        "temp_c": weather_data.get('temperature_2m'),
        "humidity_pct": weather_data.get('relative_humidity_2m'),
        "pressure_hpa": weather_data.get('surface_pressure'),
        "wind_speed_kmh": weather_data.get('wind_speed_10m'),
        "wind_dir_deg": weather_data.get('wind_direction_10m'),
        "rain_mm": weather_data.get('rain', 0),
        "solar_rad_wm2": weather_data.get('direct_radiation', 0),
        "inserted_at": datetime.utcnow()
    }

    # 4. Store in MongoDB if connected
    if feature_store is not None:
        print("\n[4/4] Storing data in MongoDB...")
        result = feature_store.update_one(
            {'timestamp': ts, 'district': selected_district},
            {'$set': record},
            upsert=True
        )
        if result.upserted_id:
            print(f"   ✓ New record inserted for {selected_district}")
        else:
            print(f"   ✓ Existing record updated for {selected_district}")

    print("\n" + "=" * 80)
    print(f"DATA FETCH COMPLETED FOR {selected_district.upper()}")
    print(f"   Timestamp: {dt_obj}")
    print(f"   EPA AQI Level: {record['epa_aqi']}")
    print(f"   PM2.5: {record['pm2_5']} µg/m³")
    print(f"   PM10: {record['pm10']} µg/m³")
    print(f"   Temperature: {record['temp_c']}°C")
    print(f"   Humidity: {record['humidity_pct']}%")
    print(f"   Wind Speed: {record['wind_speed_kmh']} km/h")
    print("=" * 80)

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
