import pandas as pd
from app.feature_ontology import PREFERENCE_CLUSTER_MAP


# ======================================================
# INFER CLUSTER FROM PREFERENCES
# ======================================================

def infer_cluster_from_preferences(preferences):

    if not preferences:
        return None

    for pref in preferences:

        if pref in PREFERENCE_CLUSTER_MAP:
            return PREFERENCE_CLUSTER_MAP[pref]

    return None


# ======================================================
# ANALYZE FEATURE CONSTRAINTS
# ======================================================

def analyze_feature_constraints(df: pd.DataFrame, constraints: dict):

    if not constraints:
        return {
            "valid": True,
            "remaining_cars": len(df),
            "failed_constraints": []
        }

    filtered = df.copy()
    failed = []

    for key, value in constraints.items():

        if key not in filtered.columns:
            continue

        filtered = filtered[filtered[key] >= value]

        if len(filtered) == 0:
            failed.append(key)

    return {
        "valid": len(filtered) > 0,
        "remaining_cars": len(filtered),
        "failed_constraints": failed
    }


# ======================================================
# ANALYZE HARD FILTERS
# ======================================================

def analyze_hard_filters(df: pd.DataFrame, filters: dict):

    filtered = df.copy()
    failed = []

    if filters.get("min_seat") is not None:

        filtered = filtered[filtered["SEAT"] >= filters["min_seat"]]

        if len(filtered) == 0:
            failed.append("min_seat")

    if filters.get("min_ground_clearance") is not None:

        filtered = filtered[
            filtered["GROUND CLEARANCE"] >= filters["min_ground_clearance"]
        ]

        if len(filtered) == 0:
            failed.append("min_ground_clearance")

    if filters.get("must_have_sunroof"):

        filtered = filtered[filtered["SUNROOF"] > 0]

        if len(filtered) == 0:
            failed.append("SUNROOF")

    if filters.get("must_have_wireless_tech"):

        filtered = filtered[
            (filtered["APPLE_CARPLAY"] == 2) |
            (filtered["ANDROID_AUTO"] == 2)
        ]

        if len(filtered) == 0:
            failed.append("wireless_tech")

    return {
        "valid": len(filtered) > 0,
        "remaining_cars": len(filtered),
        "failed_filters": failed
    }


# ======================================================
# ANALYZE BUDGET
# ======================================================

def analyze_budget(df: pd.DataFrame, max_budget=None, min_budget=None):

    filtered = df.copy()

    if min_budget is not None:
        filtered = filtered[filtered["HARGAOTR"] >= min_budget]

    if max_budget is not None:
        filtered = filtered[filtered["HARGAOTR"] <= max_budget]

    return {
        "remaining_cars": len(filtered),
        "valid": len(filtered) > 0
    }


# ======================================================
# MAIN CONSTRAINT ANALYZER
# ======================================================

def analyze_constraints(
        df: pd.DataFrame,
        feature_constraints=None,
        hard_filters=None,
        max_budget=None,
        min_budget=None
):

    report = {}

    report["feature_constraints"] = analyze_feature_constraints(
        df,
        feature_constraints or {}
    )

    report["hard_filters"] = analyze_hard_filters(
        df,
        hard_filters or {}
    )

    report["budget"] = analyze_budget(
        df,
        max_budget,
        min_budget
    )

    return report