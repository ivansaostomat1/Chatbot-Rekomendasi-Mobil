# backend/app/feature engineering/preprocessing.py

import os
import sys

# Path injection for app package
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

import pandas as pd
import numpy as np

from ..feature_ontology import TRANSMISSION_MAP



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

    if "CC" in df.columns:
        df["IS_TURBO"] = df["CC"].astype(str).str.contains(r't', case=False, na=False)

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

    binary_map = {
        "no": 0, "yes": 1,
        "0": 0, "1": 1,
        "": 0,
        0: 0, 1: 1,
        0.0: 0, 1.0: 1
    }

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
        "WIRELESS_CHARGER": binary_map,
        "DRIVE_SYS": {"fwd": 1, "rwd": 2, "awd": 3, "4wd": 4},
        "TRANSMISSION": TRANSMISSION_MAP,
        "POWER_TAILGATE": binary_map,

        "AMBIENT_LIGHT": binary_map,
        "HEAD_UP_DISPLAY": binary_map,
        "CAMERA_360": binary_map,
        "AUTO_HOLD": binary_map,

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
"REAR_SEAT_ENTERTAINMENT": binary_map,
"PARKING_BRAKE": {"manual": 0, "electric": 1},
"AEB": binary_map,
"ACC": binary_map,
"LKA": binary_map,
"ABS": binary_map,
"ESC": binary_map,
"TCS": binary_map,
"RCTA": binary_map,
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
# MERGE PRODUCT LIFECYCLE (dari Wholesale per Varian)
# ======================================================

def merge_product_lifecycle_safe(df, wholesales):
    """
    Menggabungkan data wholesale ke dataset mobil untuk mengekstrak Discontinue-Safe Index.

    Wholesale mencerminkan tren pemesanan dealer ke pabrik.
    Indeks ini membandingkan volume wholesale di Kuartal Akhir (Q4: Okt, Nov, Des)
    melawan 3 Kuartal sebelumnya (Q1-Q3: Jan-Sep).
      - Jika Q4 drop drastis mendekati 0 -> Sinyal model mau diskontinyu/ganti model.
      - Jika Q4 stabil atau naik -> Model aman secara product lifecycle.

    Join: BRAND + MODEL + VARIAN (level varian)
    Output: LIFECYCLE_SCORE
    """

    keys = ["BRAND", "MODEL", "VARIAN"]

    wholesales = wholesales.copy()

    # Hitung rata-rata
    q1_q3_cols = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP"]
    q4_cols = ["OCT", "NOV", "DEC"]

    for col in q1_q3_cols + q4_cols:
        wholesales[col] = safe_numeric(wholesales[col])

    wholesales["Q1_Q3_AVG"] = wholesales[q1_q3_cols].mean(axis=1)
    wholesales["Q4_AVG"] = wholesales[q4_cols].mean(axis=1)

    # Normalize keys
    for key in keys:
        wholesales[key] = wholesales[key].apply(normalize_text)
        df[key] = df[key].apply(normalize_text)

    df = df.merge(
        wholesales[keys + ["Q1_Q3_AVG", "Q4_AVG"]],
        on=keys,
        how="left"
    )

    df["Q1_Q3_AVG"] = df["Q1_Q3_AVG"].fillna(0)
    df["Q4_AVG"] = df["Q4_AVG"].fillna(0)

    # Growth / Momentum formula: ln(1 + Q4) - ln(1 + Q1_Q3)
    df["LIFECYCLE_SCORE"] = np.log1p(df["Q4_AVG"]) - np.log1p(df["Q1_Q3_AVG"])

    return df


# ======================================================
# BRAND ALIAS MAP
# Beberapa brand di mobil.csv/wholesale.csv merupakan sub-brand
# yang tidak ada di retail.csv. Mapping ini mengelompokkan
# sub-brand ke parent brand agar bisa di-join dengan data retail.
# ======================================================

BRAND_ALIAS_MAP = {
    "mercedes-amg": "mercedes-benz",
    "mercedes-maybach": "mercedes-benz",
}


def apply_brand_alias(brand: str) -> str:
    """Map sub-brand ke parent brand untuk keperluan join dengan retail."""
    return BRAND_ALIAS_MAP.get(brand, brand)


# ======================================================
# MERGE BRAND STRENGTH (dari Retail per Brand)
# ======================================================

def merge_brand_strength(df, retail):
    """
    Menggabungkan data retail ke dataset mobil.

    Retail mencerminkan penyerapan pasar aktual ke konsumen.
    Volume retail brand raksasa menciptakan "Ecosystem Strength" secara organik:
      - Harga jual kembali yang stabil
      - Jaringan aftersales independen luas
      - Komunitas yang massive (safe-choice brand)

    Join: BRAND only (retail hanya level brand)
    Output: BRAND_STRENGTH_SCORE (log-transformed total penjualan retail tahunan)

    NOTE: Sub-brand (MERCEDES-AMG, MERCEDES-MAYBACH) di-alias ke parent
          brand (MERCEDES-BENZ) agar mendapat kekuatan brand yang sama.
    """

    retail = retail.copy()

    # Normalize brand di keduanya
    retail["BRAND"] = retail["BRAND"].apply(normalize_text)
    df["BRAND"] = df["BRAND"].apply(normalize_text)

    # Buat temporary join key dengan alias mapping
    df["_BRAND_JOIN"] = df["BRAND"].apply(apply_brand_alias)
    retail["_BRAND_JOIN"] = retail["BRAND"].apply(apply_brand_alias)

    # Hitung total retail tahunan dari semua kolom bulan
    month_cols = [c for c in retail.columns if c not in ["BRAND", "_BRAND_JOIN"]]
    for col in month_cols:
        retail[col] = safe_numeric(retail[col])

    retail["RETAIL_TOTAL"] = retail[month_cols].sum(axis=1)

    # Merge per parent brand (via join key)
    df = df.merge(
        retail[["_BRAND_JOIN", "RETAIL_TOTAL"]],
        on="_BRAND_JOIN",
        how="left"
    )

    # Cleanup temporary column
    df.drop(columns=["_BRAND_JOIN"], inplace=True)

    df["RETAIL_TOTAL"] = df["RETAIL_TOTAL"].fillna(0)
    df["BRAND_STRENGTH_SCORE"] = np.log1p(df["RETAIL_TOTAL"])

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