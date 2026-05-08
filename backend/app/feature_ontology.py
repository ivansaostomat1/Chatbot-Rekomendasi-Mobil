# backend/app/feature_ontology.py

# ======================================================
# USER PREFERENCE --- INDEX MAPPING (SUPPORT LISTS)
# ======================================================

PREFERENCE_INDEX_MAP = {

    # Efficiency
    "irit": ["efficiency"],
    "hemat": ["efficiency"],
    "bbm": ["efficiency"],

    # Power & Handling (Multi-Index Support)
    "sporty": ["power", "handling", "driver_comfort"],
    "sport": ["power", "handling", "luxury"],
    "performa": ["power", "handling"],
    "kencang": ["power", "handling"],
    "ngebut": ["power"],
    "responsif": ["power"],
    "tenaga": ["power"],
    "nanjak": ["power"],

    "lincah": ["handling"],
    "gesit": ["handling"],
    "handling": ["handling"],
    "enak dikendarai": ["handling", "driver_comfort"],
    "fun": ["handling"],
    "stabil": ["handling"],

    # Comfort
    "nyaman": ["passenger_comfort", "driver_comfort"],
    "driver nyaman": ["driver_comfort"],

    # Space
    "keluarga": ["space"],
    "luas": ["space"],
    "kabinnya luas": ["space"],

    # Safety
    "aman": ["safety"],

    # Technology
    "teknologi": ["tech"],
    "fitur": ["tech"],
    "fitur lengkap": ["tech"],
    "modern": ["tech"],
    "canggih": ["tech"],

    # Luxury
    "mewah": ["luxury"],
    "luxury": ["luxury"],

    # Offroad
    "banjir": ["offroad"],
    "jalan rusak": ["offroad"],

    # Brand Strength (Ecosystem)
    "merek": ["brand_strength"],
    "brand": ["brand_strength"],
    "terkenal": ["brand_strength"],
    "laku": ["brand_strength"],
    "populer": ["brand_strength"],

    # Product Lifecycle (Discontinue-Safe)
    "model baru": ["lifecycle"],
    "baru": ["lifecycle"],
    "sparepart": ["brand_strength", "lifecycle"],
    "aman": ["safety", "brand_strength", "lifecycle"],
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
    "coupe": "SEDAN",
    "sport": "SEDAN"
}


# ======================================================
# POWERTRAIN ONTOLOGY
# ======================================================

POWERTRAIN_MAP = {
    "bensin": "Bensin",
    "gasoline": "Bensin",
    "diesel": "Diesel",
    "solar": "Diesel",
    "hybrid": "Hybrid",
    "listrik": "Listrik",
    "ev": "Listrik",
    "bev": "Listrik"
}


# ======================================================
# DRIVETRAIN ONTOLOGY
# ======================================================

DRIVETRAIN_MAP = {
    "fwd": 1,
    "rwd": 2,
    "awd": 3,
    "4wd": 4,
    "4x4": 4
}

DRIVETRAIN_DECODING = {
    1.0: "FWD",
    2.0: "RWD",
    3.0: "AWD",
    4.0: "4WD",
    4.4: "4WD" # Handling legacy float
}

DRIVETRAIN_ENCODING = {
    1: 1.0,
    2: 2.0,
    3: 3.0,
    4: 4.0,
    "FWD": 1.0,
    "RWD": 2.0,
    "AWD": 3.0,
    "4WD": 4.0
}


# ======================================================
# TRANSMISSION ONTOLOGY
# ======================================================

TRANSMISSION_MAP = {
    "mt": 1.0,
    "at": 2.0,
    "cvt": 3.0,
    "dct": 4.0,
    "single speed": 5.0,
    "dht": 6.0,
    "amt": 7.0
}

TRANSMISSION_DECODING = {
    1.0: "MT",
    2.0: "AT",
    3.0: "CVT",
    4.0: "DCT",
    5.0: "Single Speed",
    6.0: "DHT",
    7.0: "AMT"
}



# ======================================================
# FEATURE ONTOLOGY (Direct Mapping)
# ======================================================

FEATURE_CONSTRAINT_MAP = {
    "sunroof": ("SUNROOF", 1),
    "moonroof": ("SUNROOF", 1),
    "panoramic": ("SUNROOF", 2),
    "kamera 360": ("CAMERA_360", 1),
    "kamera": ("CAMERA_360", 1),
    "carplay": ("APPLE_CARPLAY", 1),
    "android auto": ("ANDROID_AUTO", 1),
    "led": ("LED_HEADLIGHT", 1),
}


# ======================================================
# HARD FILTERS (Technical constraints)
# ======================================================

HARD_FILTER_MAP = {
    "keluarga besar": {"min_seat": 7},
    "7 orang": {"exact_seat": 7},
    "7 seat": {"exact_seat": 7},
    "7 penumpang": {"exact_seat": 7},
    "5 orang": {"exact_seat": 5},
    "5 seat": {"exact_seat": 5},
    "banjir": {"min_ground_clearance": 190},
}


# ======================================================
# BRAND ONTOLOGY
# ======================================================

BRAND_MAP = {
    "toyota": "Toyota",
    "honda": "Honda",
    "suzuki": "Suzuki",
    "mitsubishi": "Mitsubishi",
    "daihatsu": "Daihatsu",
    "hyundai": "Hyundai",
    "kia": "Kia",
    "wuling": "Wuling",
    "mazda": "Mazda",
    "nissan": "Nissan"
}


# ======================================================
# GLOBAL DEFAULT WEIGHTS (Initial UI State)
# ======================================================

GLOBAL_DEFAULT_WEIGHTS = {
    "power": 5, "handling": 5, "efficiency": 5,
    "driver_comfort": 5, "passenger_comfort": 5, "safety": 5,
    "tech": 5, "space": 5, "offroad": 5,
    "luxury": 5, "lifecycle": 5, "brand_strength": 5,
    "price": 10,
}

# ======================================================
# NEED --- HARD FILTERS
# ======================================================

NEED_HARD_FILTER_MAP = {
    "keluarga": {"min_seat": 7},
    "tangguh": {"min_ground_clearance": 190}
}

# ======================================================
# UI TO INDEX BRIDGE (Critical for VIKOR Mapping)
# ======================================================

UI_TO_INDEX_MAP = {
    "power": "INDEX_POWER",
    "handling": "INDEX_HANDLING",
    "efficiency": "INDEX_EFFICIENCY",
    "driver_comfort": "INDEX_DRIVER_COMFORT",
    "passenger_comfort": "INDEX_PASSENGER_COMFORT",
    "safety": "INDEX_SAFETY",
    "tech": "INDEX_TECH",
    "space": "INDEX_SPACE",
    "offroad": "INDEX_OFFROAD",
    "luxury": "INDEX_LUXURY",
    "lifecycle": "INDEX_LIFECYCLE_SAFE",
    "brand_strength": "INDEX_BRAND_STRENGTH",
    "price": "INDEX_PRICE",
}

