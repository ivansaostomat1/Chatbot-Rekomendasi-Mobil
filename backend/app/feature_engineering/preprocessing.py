# backend/app/feature engineering/preprocessing.py

import pandas as pd
import numpy as np


def safe_numeric(series):

    series = (
        series.astype(str)
        .str.replace(r"[^\d\.]", "", regex=True)  # buang unit seperti cc, Nm, L
    )

    return pd.to_numeric(series, errors="coerce").fillna(0)


def normalize_text(x):

    if pd.isna(x):
        return ""

    return str(x).strip().lower()

# ======================================================
# DATA CLEANING LAYER
# ======================================================

def clean_numeric_columns(df):

    numeric_cols = [

        "HORSE POWER (HP)",
        "TORQUE (Nm)",
        "CC",
        "WEIGHT (GVW)",
        "BATTERY (KWH)",
        "EV_RANGE_KM",
        "TRUNK_CAPACITY_LITER",
        "WHEELBASE",
        "WIDTH",
        "HEIGHT",
        "GROUND CLEARANCE",
        "HARGAOTR"

    ]

    for col in numeric_cols:

        if col in df.columns:
            df[col] = safe_numeric(df[col])

    return df

# ======================================================
# GRANULAR ENCODING
# ======================================================

def encode_granular_features(df):

    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].apply(normalize_text)

    encoders = {

        "APPLE_CARPLAY": {"": 0, "wired": 1, "wireless": 2},

        "ANDROID_AUTO": {
            "": 0,
            "wired": 1,
            "wireless": 2,
            "built-in": 3
        },

        "SUNROOF": {"": 0, "moonroof": 1, "panoramic": 2},

        "HEADLAMP": {"halogen": 0, "led": 1, "matrix led": 2},

        "REAR_LAMP": {
            "bulb": 0,
            "halogen": 1,
            "combo led": 2,
            "led": 3
        },

        "SPEEDOMETER": {"analog": 0, "digital": 1},
        "WIRELESS_CHARGER": {"no": 0, "yes": 1},
        "DRIVE_SYS": {"fwd": 1, "rwd": 2, "awd": 3, "4wd": 4},
        "TRANSMISSION": {"mt": 1, "at": 2, "cvt": 3, "dct": 4},
        "POWER_TAILGATE": {"no": 0, "yes": 1},
        "AMBIENT_LIGHT": {"no": 0, "yes": 1},
        "HEAD_UP_DISPLAY": {"no": 0, "yes": 1},

# Untuk tipe jok (Leather/Fabric) buat skalanya
"LEATHER_SEAT": {
    "fabric": 0, 
    "recycled material": 1, 
    "synthetic leather": 2, 
    "leather": 3, 
    "nappa leather": 4, 
    "alcantara": 4
},

# Untuk electric/ventilated/massage seat buat rentang bobotnya
"ELECTRIC_SEAT": {
    "no": 0, 
    "yes (driver)": 1, 
    "yes (front)": 2, 
    "yes (front & rear backrest)": 3,
    "yes (front & rear)": 4,
    "yes (all)": 5
},
"VENTILATED_SEAT": {
    "no": 0, 
    "yes (driver)": 1, 
    "yes (front)": 2, 
    "yes (front & 2nd row)": 3, 
    "yes (front & rear)": 4,
    "yes (all)": 5
},
"MASSAGE_SEAT": {
    "no": 0, 
    "yes (driver)": 1, 
    "yes (front)": 2, 
    "yes (rear)": 2,
    "yes (front & rear)": 4
}

    }


    for col, mapping in encoders.items():

        if col in df.columns:

            df[col] = df[col].map(mapping).fillna(0).astype(float)

    return df


# ======================================================
# MERGE POPULARITY
# ======================================================

def merge_popularity(df, wholesales):

    keys = ["BRAND", "MODEL", "VARIAN"]

    wholesales["TOTAL_2025"] = safe_numeric(wholesales["TOTAL_2025"])

    # NORMALIZE KEYS DI KEDUA DATASET
    for key in keys:
        wholesales[key] = wholesales[key].apply(normalize_text)
        df[key] = df[key].apply(normalize_text)

    df = df.merge(
        wholesales[keys + ["TOTAL_2025"]],
        on=keys,
        how="left"
    )

    df["TOTAL_2025"] = df["TOTAL_2025"].fillna(0)

    df["POPULARITY_LOG"] = np.log1p(df["TOTAL_2025"])

    return df


# ======================================================
# DERIVED FEATURES
# ======================================================

def add_derived_features(df):

    df["HORSE POWER (HP)"] = safe_numeric(df["HORSE POWER (HP)"])
    df["TORQUE (Nm)"] = safe_numeric(df["TORQUE (Nm)"])
    df["CC"] = safe_numeric(df["CC"])
    df["WEIGHT (GVW)"] = safe_numeric(df["WEIGHT (GVW)"])

    df["POWER_TO_WEIGHT"] = np.where(
        df["WEIGHT (GVW)"] > 0,
        df["HORSE POWER (HP)"] / (df["WEIGHT (GVW)"] / 1000),
        0
    )

    # TAMBAHKAN INI SEBAGAI PENGGANTI TORQUE_PER_CC
    df["TORQUE_TO_WEIGHT"] = np.where(
        df["WEIGHT (GVW)"] > 0,
        df["TORQUE (Nm)"] / (df["WEIGHT (GVW)"] / 1000),
        0
    )


    df["EV_EFFICIENCY"] = np.where(
        df["BATTERY (KWH)"] > 0,
        df["EV_RANGE_KM"] / df["BATTERY (KWH)"],
        0
    )

    return df