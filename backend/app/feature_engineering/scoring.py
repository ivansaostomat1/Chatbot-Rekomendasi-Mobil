# backend/app/feature engineering/scoring.py

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

    return pd.concat(zlist, axis=1).mean(axis=1)


# ======================================================
# INDEX CALCULATION
# ======================================================

def calculate_indices(df):

    df["INDEX_DRIVER_COMFORT"] = build_index(df, [
        "TILT_TELESCOPIC_STEERING", "ELECTRIC_SEAT", "LEATHER_SEAT", 
        "VENTILATED_SEAT", "MASSAGE_SEAT", "HEAD_UP_DISPLAY", 
        "WIRELESS_CHARGER", "AUTO_HOLD", "DRIVER_MONITOR_CAMERA"
    ])

    df["INDEX_PASSENGER_COMFORT"] = build_index(df, [
        "LEATHER_SEAT", "ELECTRIC_SEAT", "VENTILATED_SEAT", 
        "MASSAGE_SEAT", "REAR_SEAT_ENTERTAINMENT", "SUNROOF", 
        "AMBIENT_LIGHT", "SOFT_TOUCH_INTERIOR", "SOFT_CLOSE_DOOR", "AIR_SUSPENSION"
    ])
    
    # Fun to Drive (Gantikan atau perkaya Index Performance)
    df["INDEX_FUN_TO_DRIVE"] = build_index(df, [
        "DRIVE_SYS", "CHASSIS", "WHEELBASE", "WEIGHT (GVW)", 
        "POWER_TO_WEIGHT", "TORQUE_TO_WEIGHT" 
    ], inverse=["WEIGHT (GVW)"]) # Berat dibalik karena makin ringan makin lincah

    df["INDEX_PERFORMANCE"] = build_index(df, [
        "HORSE POWER (HP)",
        "TORQUE (Nm)",
        "POWER_TO_WEIGHT",
        "TORQUE_TO_WEIGHT",
        "GROUND CLEARANCE"  # Disesuaikan dengan header asli dataset mobil.csv
    ])

    # --------------------------------------------------
    # PEMISAHAN PERHITUNGAN EFISIENSI (EV vs ICE)
    # --------------------------------------------------
    df["INDEX_EFFICIENCY"] = 0.0
    
    # Deteksi kendaraan EV berdasarkan kapasitas baterai
    is_ev = df["BATTERY (KWH)"] > 0

    # 1. Hitung Efisiensi untuk Mobil ICE (Bensin/Diesel)
    # Asumsi ICE Irit: CC kecil dan Bobot ringan
    if (~is_ev).any():
        z_cc_ice = -zscore(df.loc[~is_ev, "CC"])
        z_weight_ice = -zscore(df.loc[~is_ev, "WEIGHT (GVW)"])
        df.loc[~is_ev, "INDEX_EFFICIENCY"] = (z_cc_ice + z_weight_ice) / 2

    # 2. Hitung Efisiensi untuk Mobil EV (Listrik)
    # Asumsi EV Irit: Range/kWh besar dan Bobot ringan
    if is_ev.any():
        z_ev_eff = zscore(df.loc[is_ev, "EV_EFFICIENCY"])
        z_weight_ev = -zscore(df.loc[is_ev, "WEIGHT (GVW)"])
        df.loc[is_ev, "INDEX_EFFICIENCY"] = (z_ev_eff + z_weight_ev) / 2
    # --------------------------------------------------

    df["INDEX_SAFETY"] = build_index(df, [
        "AIRBAGS",
        "ABS",
        "ESC",
        "AEB",
        "ACC",
        "LKA",
        "RCTA"
    ])

    df["INDEX_TECH"] = build_index(df, [
        "APPLE_CARPLAY",
        "ANDROID_AUTO",
        "HEAD_UP_DISPLAY",
        "WIRELESS_CHARGER",
        "DRIVER_MONITOR_CAMERA",
        "CAMERA_360"
    ])

    df["INDEX_SPACE"] = build_index(df, [
        "SEAT",
        "TRUNK_CAPACITY_LITER",
        "WHEELBASE",
        "WIDTH",
        "HEIGHT"
    ])

    df["INDEX_OFFROAD"] = build_index(df, [
        "GROUND CLEARANCE", # Disesuaikan dengan header asli dataset
        "DRIVE_SYS",
        "TORQUE (Nm)",
        "WHEELBASE"
    ])

    df["INDEX_LUXURY"] = build_index(df, [
        "LEATHER_SEAT",
        "VENTILATED_SEAT",
        "MASSAGE_SEAT",
        "ELECTRIC_SEAT",
        "SUNROOF",
        "HEAD_UP_DISPLAY",
        "AMBIENT_LIGHT",
        "CAMERA_360",
        "WIRELESS_CHARGER"
    ])

    df["INDEX_POPULARITY"] = zscore(df["POPULARITY_LOG"])

    df["INDEX_PRICE"] = -zscore(df["HARGAOTR"])

    return df