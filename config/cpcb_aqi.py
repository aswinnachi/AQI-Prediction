"""
Official Central Pollution Control Board (CPCB) & Indian National AQI (NAQI) Engine
Implements standard breakpoints and sub-index calculation algorithms defined by
the Ministry of Environment, Forest and Climate Change (MoEFCC), Government of India.
"""
import math

# Official CPCB Breakpoints: (B_lo, B_hi, I_lo, I_hi)
CPCB_BREAKPOINTS = {
    'pm2_5': [
        (0.0, 30.0, 0, 50),       # Good
        (30.1, 60.0, 51, 100),    # Satisfactory
        (60.1, 90.0, 101, 200),   # Moderate
        (90.1, 120.0, 201, 300),  # Poor
        (120.1, 250.0, 301, 400), # Very Poor
        (250.1, 500.0, 401, 500)  # Severe
    ],
    'pm10': [
        (0.0, 50.0, 0, 50),
        (50.1, 100.0, 51, 100),
        (100.1, 250.0, 101, 200),
        (250.1, 350.0, 201, 300),
        (350.1, 430.0, 301, 400),
        (430.1, 600.0, 401, 500)
    ],
    'no2': [
        (0.0, 40.0, 0, 50),
        (40.1, 80.0, 51, 100),
        (80.1, 180.0, 101, 200),
        (180.1, 280.0, 201, 300),
        (280.1, 400.0, 301, 400),
        (400.1, 600.0, 401, 500)
    ],
    'so2': [
        (0.0, 40.0, 0, 50),
        (40.1, 80.0, 51, 100),
        (80.1, 380.0, 101, 200),
        (380.1, 800.0, 201, 300),
        (800.1, 1600.0, 301, 400),
        (1600.1, 2400.0, 401, 500)
    ],
    'co': [
        (0.0, 1.0, 0, 50),
        (1.01, 2.0, 51, 100),
        (2.01, 10.0, 101, 200),
        (10.01, 17.0, 201, 300),
        (17.01, 34.0, 301, 400),
        (34.01, 50.0, 401, 500)
    ],
    'o3': [
        (0.0, 50.0, 0, 50),
        (50.1, 100.0, 51, 100),
        (100.1, 168.0, 101, 200),
        (168.1, 208.0, 201, 300),
        (208.1, 748.0, 301, 400),
        (748.1, 1000.0, 401, 500)
    ]
}

# Categories, Color Codes & Public Health Advisories (Official CPCB / TNPCB)
INDIAN_AQI_CATEGORIES = {
    'Good': {
        'level': 1,
        'color': '#059669',     # Green
        'badge': '🟢 Good',
        'range': '0 - 50',
        'health_impact': 'Minimal impact. Air quality is clean and healthy for all activities.'
    },
    'Satisfactory': {
        'level': 2,
        'color': '#84cc16',     # Lime Green
        'badge': '🟡 Satisfactory',
        'range': '51 - 100',
        'health_impact': 'Minor breathing discomfort to sensitive individuals. Clean for the general public.'
    },
    'Moderate': {
        'level': 3,
        'color': '#f59e0b',     # Amber
        'badge': '🟠 Moderate',
        'range': '101 - 200',
        'health_impact': 'Breathing discomfort to people with asthma, heart condition, children and elderly.'
    },
    'Poor': {
        'level': 4,
        'color': '#f97316',     # Orange/Red
        'badge': '🔴 Poor',
        'range': '201 - 300',
        'health_impact': 'Breathing discomfort to most people on prolonged outdoor exposure.'
    },
    'Very Poor': {
        'level': 5,
        'color': '#dc2626',     # Red
        'badge': '🟣 Very Poor',
        'range': '301 - 400',
        'health_impact': 'Respiratory illness to people on prolonged exposure. Vulnerable groups stay indoors.'
    },
    'Severe': {
        'level': 6,
        'color': '#7f1d1d',     # Dark Crimson
        'badge': '🟤 Severe',
        'range': '401 - 500',
        'health_impact': 'Emergency condition. Affects healthy people and seriously impacts those with existing ailments.'
    }
}

def calculate_sub_index(conc, pollutant):
    """Calculate pollutant sub-index using CPCB linear interpolation formula"""
    if conc is None or conc < 0:
        return 0.0
    
    # If CO is in µg/m³, convert to mg/m³
    if pollutant == 'co' and conc > 50:
        conc = conc / 1000.0

    breakpoints = CPCB_BREAKPOINTS.get(pollutant, [])
    for b_lo, b_hi, i_lo, i_hi in breakpoints:
        if b_lo <= conc <= b_hi:
            return i_lo + ((i_hi - i_lo) / (b_hi - b_lo)) * (conc - b_lo)
            
    # Beyond highest breakpoint
    if breakpoints:
        last = breakpoints[-1]
        if conc > last[1]:
            return 500.0
            
    return 0.0

def calculate_cpcb_aqi(pm25, pm10=None, no2=None, so2=None, co=None, o3=None):
    """
    Calculate overall Indian CPCB Air Quality Index & Prominent Pollutant
    Returns dict: {'aqi', 'category', 'level', 'color', 'badge', 'prominent_pollutant', 'health_impact'}
    """
    sub_indices = {}
    
    if pm25 is not None:
        sub_indices['PM2.5'] = calculate_sub_index(pm25, 'pm2_5')
    if pm10 is not None:
        sub_indices['PM10'] = calculate_sub_index(pm10, 'pm10')
    if no2 is not None:
        sub_indices['NO2'] = calculate_sub_index(no2, 'no2')
    if so2 is not None:
        sub_indices['SO2'] = calculate_sub_index(so2, 'so2')
    if co is not None:
        sub_indices['CO'] = calculate_sub_index(co, 'co')
    if o3 is not None:
        sub_indices['O3'] = calculate_sub_index(o3, 'o3')
        
    if not sub_indices:
        return {
            'aqi': 50,
            'category': 'Good',
            'level': 1,
            'color': '#059669',
            'badge': '🟢 Good',
            'prominent_pollutant': 'N/A',
            'health_impact': 'Normal air conditions.'
        }
        
    # Primary rule: Overall AQI is maximum sub-index
    prominent = max(sub_indices, key=sub_indices.get)
    overall_aqi = round(sub_indices[prominent])
    overall_aqi = max(1, min(500, overall_aqi))
    
    # Categorize
    if overall_aqi <= 50:
        cat_name = 'Good'
    elif overall_aqi <= 100:
        cat_name = 'Satisfactory'
    elif overall_aqi <= 200:
        cat_name = 'Moderate'
    elif overall_aqi <= 300:
        cat_name = 'Poor'
    elif overall_aqi <= 400:
        cat_name = 'Very Poor'
    else:
        cat_name = 'Severe'
        
    cat_info = INDIAN_AQI_CATEGORIES[cat_name]
    
    return {
        'aqi': overall_aqi,
        'category': cat_name,
        'level': cat_info['level'],
        'color': cat_info['color'],
        'badge': cat_info['badge'],
        'prominent_pollutant': prominent,
        'health_impact': cat_info['health_impact'],
        'sub_indices': {k: round(v, 1) for k, v in sub_indices.items()}
    }

def get_cpcb_category_from_aqi(aqi_val):
    """
    Map any numeric AQI score (0-500) to its official CPCB Category, badge, color,
    and public health advisory.
    """
    if aqi_val is None:
        aqi_val = 50.0
    try:
        val = float(aqi_val)
        if math.isnan(val):
            val = 50.0
    except (ValueError, TypeError):
        val = 50.0
        
    val = round(max(0, min(500, val)))
    
    if val <= 50:
        cat_name = 'Good'
    elif val <= 100:
        cat_name = 'Satisfactory'
    elif val <= 200:
        cat_name = 'Moderate'
    elif val <= 300:
        cat_name = 'Poor'
    elif val <= 400:
        cat_name = 'Very Poor'
    else:
        cat_name = 'Severe'
        
    cat_info = INDIAN_AQI_CATEGORIES[cat_name]
    return {
        'aqi': val,
        'category': cat_name,
        'level': cat_info['level'],
        'color': cat_info['color'],
        'badge': cat_info['badge'],
        'range': cat_info['range'],
        'health_impact': cat_info['health_impact']
    }
