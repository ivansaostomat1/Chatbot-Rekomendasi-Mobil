# backend/app/feature_engineering/scoring.py

import os
import sys

# Path injection for app package
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

import pandas as pd
import numpy as np


def safe_numeric(series):
    return pd.to_numeric(series, errors="coerce").fillna(0)


def clip_outliers(series, lower=0.01, upper=0.99):

    series = safe_numeric(series)

    low = series.quantile(lower)
    high = series.quantile(upper)

    return series.clip(low, high)


def zscore(series):

    series = clip_outliers(series)

    std = series.std()

    if std == 0 or np.isnan(std):
        return pd.Series(0, index=series.index)

    return (series - series.mean()) / std


def scale_1_to_10(series):
    """
    Mengubah distribusi data apapun (Z-score, dll) menjadi skala linear 1-10.
    1 = Terburuk di kelasnya, 10 = Terbaik di kelasnya.
    """
    s_min = series.min()
    s_max = series.max()
    
    if s_max == s_min:
        return pd.Series(5.0, index=series.index)
        
    return 1 + (series - s_min) * (10 - 1) / (s_max - s_min)


# ======================================================
# INDEX BUILDER
# ======================================================

def build_index(df, cols, inverse=None):

    if inverse is None:
        inverse = []

    zlist = []

    for col in cols:

        if col not in df.columns:
            continue

        z = zscore(df[col])

        if col in inverse:
            z = -z

        zlist.append(z)

    if len(zlist) == 0:
        return pd.Series(0, index=df.index)

    # Rata-rata Z-score (masih dalam distribusi statistik)
    return pd.concat(zlist, axis=1).mean(axis=1)


# ======================================================
# INDEX CALCULATION
# ======================================================

def calculate_indices(df):

    # 1. DRIVER COMFORT
    df["INDEX_DRIVER_COMFORT"] = build_index(df, [
        "TILT_TELESCOPIC_STEERING", "ELECTRIC_SEAT", "LEATHER_SEAT", 
        "VENTILATED_SEAT", "MASSAGE_SEAT", "HEAD_UP_DISPLAY", 
        "WIRELESS_CHARGER", "AUTO_HOLD", "DRIVER_MONITOR_CAMERA"
    ])

    # 2. PASSENGER COMFORT
    df["INDEX_PASSENGER_COMFORT"] = build_index(df, [
        "LEATHER_SEAT", "ELECTRIC_SEAT", "VENTILATED_SEAT", 
        "MASSAGE_SEAT", "REAR_SEAT_ENTERTAINMENT", "SUNROOF", 
        "AMBIENT_LIGHT", "SOFT_TOUCH_INTERIOR", "SOFT_CLOSE_DOOR", "AIR_SUSPENSION"
    ])
    
    # 3. RAW POWER (Tenaga Mentah)
    df["INDEX_POWER"] = build_index(df, [
        "HORSE POWER (HP)",
        "TORQUE (Nm)",
        "POWER_TO_WEIGHT",
        "TORQUE_TO_WEIGHT"
    ])

    # 4. HANDLING & AGILITY (Kelincahan & Stabilitas)
    df["INDEX_HANDLING"] = build_index(df, [
        "GROUND CLEARANCE",
        "WEIGHT (GVW)",
        "POWER_TO_WEIGHT"
    ], inverse=["GROUND CLEARANCE", "WEIGHT (GVW)"])

    # 5. EFFICIENCY (EV vs ICE)
    df["INDEX_EFFICIENCY"] = 0.0
    is_ev = df["BATTERY (KWH)"] > 0
    if (~is_ev).any():
        z_cc_ice = -zscore(df.loc[~is_ev, "CC"])
        z_weight_ice = -zscore(df.loc[~is_ev, "WEIGHT (GVW)"])
        df.loc[~is_ev, "INDEX_EFFICIENCY"] = (z_cc_ice + z_weight_ice) / 2
    if is_ev.any():
        z_ev_eff = zscore(df.loc[is_ev, "EV_EFFICIENCY"])
        z_weight_ev = -zscore(df.loc[is_ev, "WEIGHT (GVW)"])
        df.loc[is_ev, "INDEX_EFFICIENCY"] = (z_ev_eff + z_weight_ev) / 2

    # 6. SAFETY
    df["INDEX_SAFETY"] = build_index(df, ["AIRBAGS", "ABS", "ESC", "AEB", "ACC", "LKA", "RCTA"])

    # 7. TECH
    df["INDEX_TECH"] = build_index(df, ["APPLE_CARPLAY", "ANDROID_AUTO", "HEAD_UP_DISPLAY", "WIRELESS_CHARGER", "CAMERA_360"])

    # 8. SPACE
    df["INDEX_SPACE"] = build_index(df, ["SEAT", "TRUNK_CAPACITY_LITER", "WHEELBASE", "WIDTH", "HEIGHT"])

    # 9. OFFROAD
    df["INDEX_OFFROAD"] = build_index(df, ["GROUND CLEARANCE", "DRIVE_SYS", "TORQUE (Nm)"])

    # 10. LUXURY
    df["INDEX_LUXURY"] = build_index(df, ["LEATHER_SEAT", "VENTILATED_SEAT", "MASSAGE_SEAT", "SUNROOF"])

    # 11. PRODUCT LIFECYCLE SAFE (dari Tren Wholesale Q4 vs Q1-Q3)
    # Tinggi = stabil/tumbuh di akhir tahun = opsi aman diskontinyu
    df["INDEX_LIFECYCLE_SAFE"] = zscore(df["LIFECYCLE_SCORE"])

    # 12. BRAND ECOSYSTEM STRENGTH (dari Retail per Brand)
    # Tinggi = volume besar beredar = komunitas massal & aftersales kuat
    df["INDEX_BRAND_STRENGTH"] = zscore(df["BRAND_STRENGTH_SCORE"])

    # 12. PRICE (Smaller Harga = Higher Index)
    df["INDEX_PRICE"] = -zscore(df["HARGAOTR"])

    # ==================================================
    # PENYERAGAMAN SKALA (LINEAR 1-10)
    # ==================================================
    # Ini memastikan semua kriteria memiliki "daya ungkit" yang sama di VIKOR.
    index_cols = [c for c in df.columns if c.startswith("INDEX_")]
    for col in index_cols:
        df[col] = scale_1_to_10(df[col])

    return df