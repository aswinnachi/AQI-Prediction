"""
Tamil Nadu Districts Coordinates and Environmental Metadata
Covers all 38 districts of Tamil Nadu, India.
"""

TN_DISTRICTS = {
    "Chennai": {
        "lat": 13.0827,
        "lon": 80.2707,
        "region": "Northern Coastal",
        "description": "State Capital & Coastal Metro",
        "major_sources": "Vehicular emissions, port activities, thermal power plants, industrial corridors"
    },
    "Coimbatore": {
        "lat": 11.0168,
        "lon": 76.9558,
        "region": "Western",
        "description": "Textile & Engineering Manufacturing Hub",
        "major_sources": "Textile processing, foundries, vehicular traffic, quarry dust"
    },
    "Madurai": {
        "lat": 9.9252,
        "lon": 78.1198,
        "region": "Southern",
        "description": "Cultural Capital & Commercial Center",
        "major_sources": "Automobile traffic, biomass burning, small-scale industries"
    },
    "Tiruchirappalli (Trichy)": {
        "lat": 10.7905,
        "lon": 78.7047,
        "region": "Central",
        "description": "Heavy Engineering & Central Hub",
        "major_sources": "Heavy fabrication (BHEL), cement transport, urban traffic"
    },
    "Salem": {
        "lat": 11.6643,
        "lon": 78.1460,
        "region": "Western",
        "description": "Steel, Sago & Mineral Processing Hub",
        "major_sources": "Steel plants, magnesite mining, sago factories, truck transit"
    },
    "Tiruppur": {
        "lat": 11.1085,
        "lon": 77.3411,
        "region": "Western",
        "description": "Knitwear & Textile Export Capital",
        "major_sources": "Dyeing/bleaching units, garment factories, diesel generators"
    },
    "Tirunelveli": {
        "lat": 8.7139,
        "lon": 77.7567,
        "region": "Southern",
        "description": "Educational & Agro-Industrial Center",
        "major_sources": "Wind dust, lime kilns, intercity transport"
    },
    "Vellore": {
        "lat": 12.9165,
        "lon": 79.1325,
        "region": "Northern",
        "description": "Leather Tannery & Medical Hub",
        "major_sources": "Tanneries, chemical processing, highway transit (NH 48)"
    },
    "Erode": {
        "lat": 11.3410,
        "lon": 77.7172,
        "region": "Western",
        "description": "Turmeric City & Textile Processing Hub",
        "major_sources": "Textile processing, paper mills, leather tanning"
    },
    "Thanjavur": {
        "lat": 10.7870,
        "lon": 79.1378,
        "region": "Delta",
        "description": "Granary of South India (Agrarian)",
        "major_sources": "Agricultural crop residue burning, dust, river basin winds"
    },
    "Dindigul": {
        "lat": 10.3673,
        "lon": 77.9803,
        "region": "Central / Southern",
        "description": "Locks & Leather Processing Center",
        "major_sources": "Leather tanning, agro-processing, highway traffic"
    },
    "Kanchipuram": {
        "lat": 12.8342,
        "lon": 79.7036,
        "region": "Northern",
        "description": "Silk City & Automotive Corridor",
        "major_sources": "Automobile manufacturing belt (Sriperumbudur), highway traffic"
    },
    "Cuddalore": {
        "lat": 11.7480,
        "lon": 79.7714,
        "region": "Central Coastal",
        "description": "Chemical & Thermal Energy Industrial Estate (SIPCOT)",
        "major_sources": "Chemical SIPCOT industries, Neyveli lignite emissions, maritime salt"
    },
    "Karur": {
        "lat": 10.9601,
        "lon": 78.0766,
        "region": "Central",
        "description": "Home Textiles & Bus Body Building Hub",
        "major_sources": "Textile export units, metal fabrication, vehicular movement"
    },
    "Thoothukudi (Tuticorin)": {
        "lat": 8.7642,
        "lon": 78.1348,
        "region": "Southern Coastal",
        "description": "Major Sea Port & Heavy Chemical / Power Cluster",
        "major_sources": "Thermal power stations, chemical fertilizer plants, port cargo"
    },
    "Kanyakumari (Nagercoil)": {
        "lat": 8.1833,
        "lon": 77.4119,
        "region": "Southernmost Coastal",
        "description": "Coastal & Tourism Zone",
        "major_sources": "Sea breeze aerosol, tourism vehicular traffic, coir processing"
    },
    "Krishnagiri (Hosur)": {
        "lat": 12.7409,
        "lon": 77.8253,
        "region": "North-Western",
        "description": "EV & Automotive Tech Industrial Gateway",
        "major_sources": "Electronics manufacturing, EV clusters, border corridor transit"
    },
    "Dharmapuri": {
        "lat": 12.1211,
        "lon": 78.1582,
        "region": "North-Western",
        "description": "Horticulture & Mineral Zone",
        "major_sources": "Granite quarrying, agricultural dust, highway transport"
    },
    "Namakkal": {
        "lat": 11.2189,
        "lon": 78.1674,
        "region": "Western",
        "description": "Poultry & Heavy Truck Transport Capital",
        "major_sources": "Heavy fleet logistics, poultry processing, lorry body building"
    },
    "Nilgiris (Ooty)": {
        "lat": 11.4102,
        "lon": 76.6950,
        "region": "Western Ghats",
        "description": "Hill Station & Biosphere Reserve",
        "major_sources": "Tourist vehicular transit, biomass heating in winter"
    },
    "Nagapattinam": {
        "lat": 10.7672,
        "lon": 79.8449,
        "region": "Delta Coastal",
        "description": "Coastal Fishing & Port Hub",
        "major_sources": "Marine aerosol, fish processing, coastal winds"
    },
    "Thiruvarur": {
        "lat": 10.7725,
        "lon": 79.6365,
        "region": "Delta",
        "description": "Agrarian Heart of Kaveri Basin",
        "major_sources": "Paddy straw burning, farm operations, seasonal dust"
    },
    "Pudukkottai": {
        "lat": 10.3797,
        "lon": 78.8208,
        "region": "Central",
        "description": "Agro-forestry & Quarrying Zone",
        "major_sources": "Stone crushing, small industries, rural biomass"
    },
    "Sivaganga": {
        "lat": 9.8433,
        "lon": 78.4809,
        "region": "Southern",
        "description": "Chettinad Heritage & Mineral Belt",
        "major_sources": "Graphite mining, brick kilns, rural dust"
    },
    "Ramanathapuram": {
        "lat": 9.3639,
        "lon": 78.8395,
        "region": "Southern Coastal",
        "description": "Dry Coastal & Marine Belt",
        "major_sources": "Wind-blown saline dust, solar parks, fishing traffic"
    },
    "Virudhunagar": {
        "lat": 9.5872,
        "lon": 77.9515,
        "region": "Southern",
        "description": "Pyrotechnics, Printing & Match Industry (Sivakasi)",
        "major_sources": "Fireworks manufacturing, offset printing inks, chemical fumes"
    },
    "Theni": {
        "lat": 10.0104,
        "lon": 77.4768,
        "region": "Western Ghats Foothills",
        "description": "Cardamom & Agricultural Valley",
        "major_sources": "Agricultural transport, agro-chemicals, mountain valley inversion"
    },
    "Tiruvannamalai": {
        "lat": 12.2253,
        "lon": 79.0747,
        "region": "Northern",
        "description": "Spiritual Hub & Agrarian Zone",
        "major_sources": "Pilgrimage transport, rice mills, agricultural dust"
    },
    "Viluppuram": {
        "lat": 11.9401,
        "lon": 79.4861,
        "region": "Northern",
        "description": "Transit Hub & Agricultural Center",
        "major_sources": "National highway corridor (NH 32 / NH 45), sugar mills"
    },
    "Kallakurichi": {
        "lat": 11.7384,
        "lon": 78.9639,
        "region": "Northern Central",
        "description": "Sugar Belt & Agricultural Basin",
        "major_sources": "Sugar mills, biomass combustion, rural road dust"
    },
    "Ranipet": {
        "lat": 12.9224,
        "lon": 79.3326,
        "region": "Northern",
        "description": "Heavy Industrial & Chemical Complex",
        "major_sources": "Chemical factories, chromium legacy sites, industrial machinery"
    },
    "Tirupathur": {
        "lat": 12.4958,
        "lon": 78.5678,
        "region": "Northern",
        "description": "Footwear & Leather Goods Belt",
        "major_sources": "Tanneries, footwear manufacturing, transport"
    },
    "Chengalpattu": {
        "lat": 12.6825,
        "lon": 79.9836,
        "region": "Northern Coastal",
        "description": "Industrial Corridor (Mahindra World City) & IT SEZs",
        "major_sources": "Auto manufacturing, IT corridor traffic, suburban construction"
    },
    "Tiruvallur": {
        "lat": 13.1432,
        "lon": 79.9083,
        "region": "Northern",
        "description": "Heavy Industrial & Thermal Power Belt (Ennore)",
        "major_sources": "Ennore thermal power, petroleum refineries, heavy commercial transit"
    },
    "Ariyalur": {
        "lat": 11.1401,
        "lon": 79.0786,
        "region": "Central",
        "description": "Cement Capital of Tamil Nadu",
        "major_sources": "Limestone mining, cement manufacturing plants, heavy truck convoys"
    },
    "Perambalur": {
        "lat": 11.2342,
        "lon": 78.8820,
        "region": "Central",
        "description": "Maize & Cotton Agrarian Belt",
        "major_sources": "Agricultural biomass burning, sugar factories, highway transit"
    },
    "Mayiladuthurai": {
        "lat": 11.1075,
        "lon": 79.6522,
        "region": "Delta Coastal",
        "description": "Coastal Kaveri Delta Center",
        "major_sources": "Paddy harvesting dust, coastal humidity aerosol, religious tourism"
    },
    "Tenkasi": {
        "lat": 8.9594,
        "lon": 77.3150,
        "region": "Western Ghats Foothills",
        "description": "Courtallam Falls & Tourism Gateway",
        "major_sources": "Seasonal tourist traffic, wood seasoning, agricultural dust"
    }
}

DEFAULT_DISTRICT = "Chennai"
