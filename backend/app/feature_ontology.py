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
}


# ======================================================
# BODY TYPE ONTOLOGY
# ======================================================

BODY_TYPE_MAP = {

    "suv": "SUV",
    "mpv": "MPV",
    "sedan": "SEDAN",

    "coupe": "SPORT",
    "roadster": "SPORT",
    "convertible": "SPORT",

    "hatchback": "SMALL",
    "city car": "SMALL",

    "wagon": "WAGON"
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

    "electric": "EV",
    "ev": "EV",
    "listrik": "EV"
}


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

    "360 camera": ("CAMERA_360", 1)
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