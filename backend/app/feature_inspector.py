# backend/app/feature_inspector.py

import pandas as pd


# ======================================================
# FEATURE COLUMNS YANG PERLU DIAWASI
# ======================================================

FEATURE_COLUMNS = [

    "SUNROOF",
    "VENTILATED_SEAT",
    "MASSAGE_SEAT",
    "ELECTRIC_SEAT",
    "LEATHER_SEAT",

    "APPLE_CARPLAY",
    "ANDROID_AUTO",
    "WIRELESS_CHARGER",

    "HEAD_UP_DISPLAY",
    "CAMERA_360",
    "DRIVER_MONITOR_CAMERA",

    "AIR_SUSPENSION",
    "SOFT_CLOSE_DOOR",
    "AMBIENT_LIGHT"
]


# ======================================================
# FEATURE COVERAGE ANALYSIS
# ======================================================

def analyze_feature_coverage(df: pd.DataFrame):

    """
    Menghitung berapa banyak mobil yang memiliki fitur tertentu
    """

    result = {}

    total_cars = len(df)

    for col in FEATURE_COLUMNS:

        if col not in df.columns:
            continue

        feature_values = pd.to_numeric(df[col], errors="coerce").fillna(0)

        count_available = (feature_values > 0).sum()

        coverage = count_available / total_cars

        result[col] = {
            "available_count": int(count_available),
            "coverage_ratio": round(float(coverage), 3)
        }

    return result


# ======================================================
# DETECT RARE FEATURES
# ======================================================

def detect_rare_features(df: pd.DataFrame, threshold=0.05):

    """
    Mendeteksi fitur yang sangat jarang di dataset
    """

    coverage = analyze_feature_coverage(df)

    rare = {}

    for feature, data in coverage.items():

        if data["coverage_ratio"] <= threshold:
            rare[feature] = data

    return rare


# ======================================================
# FEATURE VALUE DISTRIBUTION
# ======================================================

def feature_value_distribution(df: pd.DataFrame):

    """
    Menghitung distribusi nilai fitur
    contoh:
    SUNROOF = {0: 330, 1: 58, 2: 221}
    """

    distributions = {}

    for col in FEATURE_COLUMNS:

        if col not in df.columns:
            continue

        value_counts = df[col].value_counts().to_dict()

        distributions[col] = value_counts

    return distributions


# ======================================================
# FEATURE COMBINATION COUNT
# ======================================================

def count_feature_combination(df: pd.DataFrame, constraints: dict):

    """
    Menghitung jumlah mobil yang memenuhi kombinasi fitur tertentu
    """

    filtered = df.copy()

    for key, value in constraints.items():

        if key not in filtered.columns:
            continue

        filtered = filtered[filtered[key] >= value]

    return len(filtered)


# ======================================================
# FEATURE SUMMARY
# ======================================================

def generate_feature_summary(df: pd.DataFrame):

    """
    Ringkasan lengkap fitur dataset
    """

    summary = {}

    summary["total_cars"] = len(df)

    summary["coverage"] = analyze_feature_coverage(df)

    summary["rare_features"] = detect_rare_features(df)

    summary["distributions"] = feature_value_distribution(df)

    return summary