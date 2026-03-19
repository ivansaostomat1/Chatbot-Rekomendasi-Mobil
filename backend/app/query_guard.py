# backend/app/query_guard.py

import pandas as pd
from typing import Optional


# ======================================================
# BODY TYPE NORMALIZATION
# ======================================================

BODY_GROUP = {
    "suv": "SUV",
    "mpv": "MPV",
    "sedan": "SEDAN",
    "coupe": "SPORT",
    "convertible": "SPORT",
    "roadster": "SPORT",
    "hatchback": "SMALL",
    "city car": "SMALL",
    "station wagon": "WAGON",
    "crossover": "SUV"
}


def normalize_body_type(df: pd.DataFrame):

    df = df.copy()

    if "BODY TYPE" not in df.columns:
        return df

    df["BODY TYPE"] = df["BODY TYPE"].astype(str).str.lower()

    df["BODY_GROUP"] = df["BODY TYPE"].map(BODY_GROUP).fillna("OTHER")

    return df


# ======================================================
# POWERTRAIN NORMALIZATION
# ======================================================

POWERTRAIN_MAP = {
    "petrol": "ICE",
    "diesel": "ICE",

    "hev": "HYBRID",
    "hybrid": "HYBRID",
    "mhev": "HYBRID",

    "phev": "PHEV",

    "bev": "EV",
    "electric": "EV"
}


def normalize_powertrain(df: pd.DataFrame):

    df = df.copy()

    if "FUEL" not in df.columns:
        return df

    df["FUEL"] = df["FUEL"].astype(str).str.lower()

    df["POWERTRAIN"] = df["FUEL"].map(POWERTRAIN_MAP).fillna("UNKNOWN")

    return df


# ======================================================
# APPLY VEHICLE TYPE FILTER
# ======================================================

def filter_body_type(df: pd.DataFrame, body_type: Optional[str]):

    if body_type is None:
        return df

    body_type = body_type.upper()

    if "BODY_GROUP" not in df.columns:
        return df

    filtered = df[df["BODY_GROUP"] == body_type]

    if filtered.empty:
        return df

    return filtered


# ======================================================
# APPLY POWERTRAIN FILTER
# ======================================================

def filter_powertrain(df: pd.DataFrame, powertrain: Optional[str]):

    if powertrain is None:
        return df

    powertrain = powertrain.upper()

    if "POWERTRAIN" not in df.columns:
        return df

    filtered = df[df["POWERTRAIN"] == powertrain]

    if filtered.empty:
        return df

    return filtered


# ======================================================
# FEATURE CONSTRAINT VALIDATOR
# ======================================================

def validate_feature_constraints(df: pd.DataFrame, constraints: dict):

    """
    Mengecek apakah kombinasi fitur user masih memiliki kandidat mobil
    """

    if not constraints:
        return df, False

    filtered = df.copy()

    for key, value in constraints.items():

        if key not in filtered.columns:
            continue

        filtered = filtered[filtered[key] >= value]

    if filtered.empty:
        return df, True

    return filtered, False


# ======================================================
# MAIN QUERY GUARD
# ======================================================

def apply_query_guard(df: pd.DataFrame,
                     body_type=None,
                     powertrain=None,
                     feature_constraints=None):

    """
    Pipeline proteksi sebelum ranking
    """

    df = normalize_body_type(df)

    df = normalize_powertrain(df)

    df = filter_body_type(df, body_type)

    df = filter_powertrain(df, powertrain)

    df, constraint_failed = validate_feature_constraints(
        df,
        feature_constraints
    )

    return df, constraint_failed