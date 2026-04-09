# backend/app/feature_ontology.py

# ======================================================
# USER PREFERENCE → INDEX MAPPING (SUPPORT LISTS)
# ======================================================

PREFERENCE_INDEX_MAP = {

    # Efficiency
    "irit": ["INDEX_EFFICIENCY"],
    "hemat": ["INDEX_EFFICIENCY"],
    "bbm": ["INDEX_EFFICIENCY"],

    # Power & Handling (Multi-Index Support)
    "sporty": ["INDEX_POWER", "INDEX_HANDLING", "INDEX_DRIVER_COMFORT"],
    "performa": ["INDEX_POWER", "INDEX_HANDLING"],
    "kencang": ["INDEX_POWER", "INDEX_HANDLING"],
    "ngebut": ["INDEX_POWER"],
    "responsif": ["INDEX_POWER"],
    "tenaga": ["INDEX_POWER"],
    "nanjak": ["INDEX_POWER"],

    "lincah": ["INDEX_HANDLING"],
    "gesit": ["INDEX_HANDLING"],
    "handling": ["INDEX_HANDLING"],
    "enak dikendarai": ["INDEX_HANDLING", "INDEX_DRIVER_COMFORT"],
    "fun": ["INDEX_HANDLING"],
    "stabil": ["INDEX_HANDLING"],

    # Comfort
    "nyaman": ["INDEX_PASSENGER_COMFORT"],
    "driver nyaman": ["INDEX_DRIVER_COMFORT"],

    # Space
    "keluarga": ["INDEX_SPACE"],
    "luas": ["INDEX_SPACE"],
    "kabinnya luas": ["INDEX_SPACE"],

    # Safety
    "aman": ["INDEX_SAFETY"],

    # Technology
    "teknologi": ["INDEX_TECH"],
    "fitur": ["INDEX_TECH"],
    "fitur lengkap": ["INDEX_TECH"],
    "modern": ["INDEX_TECH"],
    "canggih": ["INDEX_TECH"],

    # Luxury
    "mewah": ["INDEX_LUXURY"],
    "luxury": ["INDEX_LUXURY"],

    # Offroad
    "banjir": ["INDEX_OFFROAD"],
    "jalan rusak": ["INDEX_OFFROAD"],

    # Brand Strength (Ecosystem)
    "merek": ["INDEX_BRAND_STRENGTH"],
    "brand": ["INDEX_BRAND_STRENGTH"],
    "terkenal": ["INDEX_BRAND_STRENGTH"],
    "laku": ["INDEX_BRAND_STRENGTH"],
    "populer": ["INDEX_BRAND_STRENGTH"],

    # Product Lifecycle (Discontinue-Safe)
    "model baru": ["INDEX_LIFECYCLE_SAFE"],
    "baru": ["INDEX_LIFECYCLE_SAFE"],
    "sparepart": ["INDEX_BRAND_STRENGTH", "INDEX_LIFECYCLE_SAFE"],
    "aman": ["INDEX_SAFETY", "INDEX_BRAND_STRENGTH", "INDEX_LIFECYCLE_SAFE"],
}


# ======================================================
# BODY TYPE ONTOLOGY
# ======================================================

BODY_TYPE_MAP = {

    # MPV
    "mpv": "MPV",
    "minivan": "MPV",
    "van": "MPV",
    
    # SUV
    "suv": "SUV",
    "crossover": "SUV",
    "cuv": "SUV",
    "jip": "SUV",
    "jeep": "SUV",
    "offroad": "SUV",
    
    # Hatchback
    "hatchback": "HATCHBACK",
    "city car": "HATCHBACK",
    "compact": "HATCHBACK",
    
    # Sedan
    "sedan": "SEDAN",
    "saloon": "SEDAN",
    "coupe": "SEDAN"
}



# ======================================================
# POWERTRAIN ONTOLOGY
# ======================================================

POWERTRAIN_MAP = {

    "bensin": "ICE",
    "petrol": "ICE",
    "diesel": "ICE",

    "hybrid": "HYBRID",
    "hev": "HYBRID",
    "mhev": "HYBRID",

    "phev": "PHEV",

    "bev": "EV",
    "electric": "EV",
    "ev": "EV",
    "listrik": "EV"
}



# ======================================================
# DRIVETRAIN ONTOLOGY
# ======================================================

DRIVETRAIN_MAP = {
    "fwd": "FWD",
    "penggerak depan": "FWD",
    
    "rwd": "RWD",
    "penggerak belakang": "RWD",
    
    "awd": "AWD",
    "all wheel drive": "AWD",
    
    "4wd": "4WD",
    "4x4": "4WD"
}

# Mapping numerik hasil preprocessing (sinkron dengan preprocessing.py)
DRIVETRAIN_ENCODING = {
    "FWD": 1.0,
    "RWD": 2.0,
    "AWD": 3.0,
    "4WD": 4.0
}

# Reverse mapping untuk display
DRIVETRAIN_DECODING = {v: k for k, v in DRIVETRAIN_ENCODING.items()}



# ======================================================
# FEATURE CONSTRAINT MAP
# ======================================================

FEATURE_CONSTRAINT_MAP = {

    "sunroof": ("SUNROOF", 1),
    "moonroof": ("SUNROOF", 1),
    "panoramic": ("SUNROOF", 2),

    "ventilated seat": ("VENTILATED_SEAT", 1),
    "massage seat": ("MASSAGE_SEAT", 1),

    "apple carplay": ("APPLE_CARPLAY", 1),
    "wireless carplay": ("APPLE_CARPLAY", 2),

    "android auto": ("ANDROID_AUTO", 1),
    "wireless android auto": ("ANDROID_AUTO", 2),

    "wireless charger": ("WIRELESS_CHARGER", 1),

    "hud": ("HEAD_UP_DISPLAY", 1),
    "head up display": ("HEAD_UP_DISPLAY", 1),

    "360 camera": ("CAMERA_360", 1),
    "kamera 360": ("CAMERA_360", 1),
    
    # ADAS & Safety
    "adas": ("AEB", 1), # Simplified projection representing advanced safety
    "aeb": ("AEB", 1),
    "lka": ("LKA", 1),
    "acc": ("ACC", 1),
    
    # Comfort & Misc
    "kursi elektrik": ("ELECTRIC_SEAT", 1),
    "electric seat": ("ELECTRIC_SEAT", 1),
    "kursi pijat": ("MASSAGE_SEAT", 1),
    "pendingin jok": ("VENTILATED_SEAT", 1),
    "kulit": ("LEATHER_SEAT", 1),
    "jok kulit": ("LEATHER_SEAT", 1),
    "power tailgate": ("POWER_TAILGATE", 1),
    "pintu lipat otomatis": ("POWER_TAILGATE", 1),
    "air suspension": ("AIR_SUSPENSION", 1),
    "suspensi udara": ("AIR_SUSPENSION", 1)
}


# ======================================================
# HARD FILTER ONTOLOGY
# ======================================================

HARD_FILTER_MAP = {

    "keluarga besar": {
        "min_seat": 7
    },

    "keluarga": {
        "min_seat": 6
    },

    "keluarga kecil": {
        "min_seat": 5
    },

    "bebas banjir": {
        "min_ground_clearance": 180
    },

    "banjir": {
        "min_ground_clearance": 180
    }
}


# ======================================================
# PREFERENCE → CLUSTER MAP
# ======================================================

PREFERENCE_CLUSTER_MAP = {

    "irit": "City Car",
    "hemat": "City Car",
    "bbm": "City Car",

    "keluarga": "Family Car",
    "luas": "Family Car",

    "kencang": "Performance",
    "ngebut": "Performance",
    "responsif": "Performance",
    "sporty": "Performance",

    "banjir": "Offroad",
    "jalan rusak": "Offroad",

    "luxury": "Luxury",
    "mewah": "Luxury"
}


# ======================================================
# NEED → CLUSTER MAP (untuk need_terms yang punya cluster jelas)
# ======================================================

NEED_CLUSTER_MAP = {
    "keluarga": "Family Car",
    "keluarga besar": "Family Car",
    "keluarga kecil": "Family Car",
    "mudik": "Family Car",
    "offroad": "Offroad",
    "banjir": "Offroad",
    "bebas banjir": "Offroad",
    "mewah": "Luxury",
}


# ======================================================
# NEED → HARD FILTER MAP (untuk need_terms)
# ======================================================

NEED_HARD_FILTER_MAP = {
    "keluarga": {"min_seat": 6},
    "keluarga besar": {"min_seat": 7},
    "keluarga kecil": {"min_seat": 5},
    "offroad": {"min_ground_clearance": 180},
    "banjir": {"min_ground_clearance": 180},
    "bebas banjir": {"min_ground_clearance": 180},
}


# ======================================================
# LIFESTYLE NEEDS — ambigu, tidak punya cluster langsung
# Jika user hanya menyebut ini tanpa preference jelas → tanya prioritas
# ======================================================

LIFESTYLE_NEEDS = {
    "kuliah",
    "anak muda",
    "harian",
    "daily",
    "kantor",
    "kerja",
    "mobil kedua",
    "pemula",
    "perjalanan jauh",
}


# ======================================================
# CLUSTERED NEEDS — punya cluster & hard filter jelas
# ======================================================

CLUSTERED_NEEDS = set(NEED_CLUSTER_MAP.keys())


# ======================================================
# BRAND MAP
# ======================================================

BRAND_MAP = {

    "toyota": "toyota",
    "honda": "honda",
    "suzuki": "suzuki",
    "mitsubishi": "mitsubishi",
    "nissan": "nissan",
    "mazda": "mazda",
    "hyundai": "hyundai",
    "kia": "kia",
    "wuling": "wuling",
    "chery": "chery",

    "bmw": "bmw",

    "mercedes": "mercedes-benz",
    "mercedes benz": "mercedes-benz",
    "benz": "mercedes-benz",

    "audi": "audi",
    "lexus": "lexus",
    "volvo": "volvo"
}


# ======================================================
# CLUSTER → WEIGHT PROFILES (Initial UI State)
# ======================================================

CLUSTER_PROFILES = {
    "Family Car": {
        "INDEX_POWER": 4, "INDEX_HANDLING": 5, "INDEX_EFFICIENCY": 7,
        "INDEX_DRIVER_COMFORT": 6, "INDEX_PASSENGER_COMFORT": 8, "INDEX_SAFETY": 8,
        "INDEX_TECH": 6, "INDEX_SPACE": 9, "INDEX_OFFROAD": 2,
        "INDEX_LUXURY": 3, "INDEX_PARTS_AVAILABILITY": 9, "INDEX_MARKET_DEMAND": 7,
        "INDEX_PRICE": 10,
    },
    "City Car": {
        "INDEX_POWER": 4, "INDEX_HANDLING": 7, "INDEX_EFFICIENCY": 9,
        "INDEX_DRIVER_COMFORT": 6, "INDEX_PASSENGER_COMFORT": 7, "INDEX_SAFETY": 6,
        "INDEX_TECH": 7, "INDEX_SPACE": 5, "INDEX_OFFROAD": 1,
        "INDEX_LUXURY": 2, "INDEX_PARTS_AVAILABILITY": 8, "INDEX_MARKET_DEMAND": 8,
        "INDEX_PRICE": 10,
    },
    "Offroad": {
        "INDEX_POWER": 8, "INDEX_HANDLING": 4, "INDEX_EFFICIENCY": 3,
        "INDEX_DRIVER_COMFORT": 5, "INDEX_PASSENGER_COMFORT": 5, "INDEX_SAFETY": 7,
        "INDEX_TECH": 5, "INDEX_SPACE": 7, "INDEX_OFFROAD": 9,
        "INDEX_LUXURY": 3, "INDEX_PARTS_AVAILABILITY": 7, "INDEX_MARKET_DEMAND": 5,
        "INDEX_PRICE": 10,
    },
    "Performance": {
        "INDEX_POWER": 9, "INDEX_HANDLING": 9, "INDEX_EFFICIENCY": 3,
        "INDEX_DRIVER_COMFORT": 7, "INDEX_PASSENGER_COMFORT": 4, "INDEX_SAFETY": 6,
        "INDEX_TECH": 7, "INDEX_SPACE": 3, "INDEX_OFFROAD": 2,
        "INDEX_LUXURY": 5, "INDEX_PARTS_AVAILABILITY": 6, "INDEX_MARKET_DEMAND": 7,
        "INDEX_PRICE": 10,
    },
    "Luxury": {
        "INDEX_POWER": 7, "INDEX_HANDLING": 7, "INDEX_EFFICIENCY": 3,
        "INDEX_DRIVER_COMFORT": 9, "INDEX_PASSENGER_COMFORT": 9, "INDEX_SAFETY": 8,
        "INDEX_TECH": 9, "INDEX_SPACE": 7, "INDEX_OFFROAD": 2,
        "INDEX_LUXURY": 10, "INDEX_PARTS_AVAILABILITY": 8, "INDEX_MARKET_DEMAND": 6,
        "INDEX_PRICE": 10,
    },
}

GLOBAL_DEFAULT_PROFILE = {
    "INDEX_POWER": 5, "INDEX_HANDLING": 5, "INDEX_EFFICIENCY": 5,
    "INDEX_DRIVER_COMFORT": 5, "INDEX_PASSENGER_COMFORT": 5, "INDEX_SAFETY": 5,
    "INDEX_TECH": 5, "INDEX_SPACE": 5, "INDEX_OFFROAD": 5,
    "INDEX_LUXURY": 5, "INDEX_PARTS_AVAILABILITY": 5, "INDEX_MARKET_DEMAND": 5,
    "INDEX_PRICE": 10,
}