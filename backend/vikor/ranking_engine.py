# backend/vikor/ranking_engine.py

import os
import sys
import pandas as pd
import numpy as np

# ======================================================
# PATH INJECTION
# ======================================================

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, ".."))

if backend_dir not in sys.path:
    sys.path.append(backend_dir)

# ======================================================
# IMPORT PROJECT MODULE
# ======================================================

from app.data_loader import load_all_datasets
from app.feature_engineering.pipeline import generate_feature_dataset

from app.query_guard import apply_query_guard
from app.feature_inspector import generate_feature_summary
from app.constraint_analyzer import analyze_constraints
from .vikor import vikor_rank, validate_compromise_solution, build_weight_vector, VIKOR_CRITERIA
from app.feature_ontology import DRIVETRAIN_DECODING, TRANSMISSION_DECODING



# ======================================================
# GLOBAL STORAGE
# ======================================================

DF_CARS = None
FEATURE_SUMMARY = None


# ======================================================
# INIT DATASET
# ======================================================

def init_dataset():

    global FEATURE_SUMMARY

    mobil, wholesales, retail = load_all_datasets()

    df = generate_feature_dataset(mobil, wholesales, retail)

    if df.empty:
        raise ValueError("Dataset kosong setelah preprocessing")

    FEATURE_SUMMARY = generate_feature_summary(df)

    print("\n================ FEATURE SUMMARY ================\n")

    print("Total Cars :", FEATURE_SUMMARY["total_cars"])

    print("\nRare Features (<5% coverage):")

    for f, data in FEATURE_SUMMARY["rare_features"].items():
        print(f"{f} -> {data['coverage_ratio']*100:.1f}%")

    print("\n===============================================\n")

    return df


DF_CARS = init_dataset()


# ======================================================
# FILTER BUDGET
# ======================================================

def filter_budget(df, max_budget=None, min_budget=None):

    if min_budget is not None:
        df = df[df["HARGAOTR"] >= min_budget]

    if max_budget is not None:
        df = df[df["HARGAOTR"] <= max_budget]

    return df


# ======================================================
# FILTER BRAND
# ======================================================

def filter_brand(df, brand=None):

    if brand is None:
        return df

    filtered = df[
        df["BRAND"].fillna("").str.lower().str.strip()
        == brand.lower().strip()
    ]

    return filtered


# ======================================================
# HARD FILTERS
# ======================================================

def apply_hard_filters(df, req_kwargs: dict):

    if req_kwargs.get("min_seat") is not None:
        df = df[df["SEAT"] >= req_kwargs["min_seat"]]

    if req_kwargs.get("exact_seat") is not None:
        df = df[df["SEAT"] == req_kwargs["exact_seat"]]

    if req_kwargs.get("min_ground_clearance") is not None:
        df = df[df["GROUND CLEARANCE"] >= req_kwargs["min_ground_clearance"]]

    if req_kwargs.get("must_have_sunroof"):
        df = df[df["SUNROOF"] > 0]

    if req_kwargs.get("must_have_wireless_tech"):
        df = df[(df["APPLE_CARPLAY"] == 2) | (df["ANDROID_AUTO"] == 2)]

    if req_kwargs.get("transmission") is not None:
        df = df[df["TRANSMISSION"] == req_kwargs["transmission"]]

    return df


# ======================================================
# MAIN RECOMMENDATION ENGINE
# ======================================================

def recommend_cars(
    weight_dict=None,
    max_budget=None,
    min_budget=None,
    top_n=5,
    body_type=None,
    powertrain=None,
    drive_sys=None,
    feature_constraints=None,
    brand=None,
    negated_terms=None,
    **kwargs
):

    print("==================================================")
    print("[VIKOR RANKING ENGINE] Memulai Proses Rekomendasi")
    print(f"[VIKOR RANKING ENGINE] Weights: {weight_dict}")
    print(f"[VIKOR RANKING ENGINE] Feature Constraints: {feature_constraints}")
    print(f"[VIKOR RANKING ENGINE] Hard Filters (need_terms): {kwargs}, Budget: {min_budget} - {max_budget}")
    print(f"[VIKOR RANKING ENGINE] Pipeline Guards: Body={body_type}, Powertrain={powertrain}, Drive={drive_sys}")

    feature_constraints = feature_constraints or {}
    weight_dict = weight_dict or {}

    df = DF_CARS.copy()
    print(f"[VIKOR RANKING ENGINE] Dataset awal: {len(df)} baris")

    # ==================================================
    # PIPELINE WITH RELAXATION STRATEGY
    # ==================================================

    def apply_pipeline(run_params: dict, analyze=False):
        nonlocal feature_constraints
        temp_df = df.copy()
        
        # 1. Query Guard
        temp_df, constraint_failed = apply_query_guard(
            temp_df,
            body_type=run_params.get("body_type"),
            powertrain=run_params.get("powertrain"),
            drive_sys=run_params.get("drive_sys"),
            feature_constraints=feature_constraints,
            negated_terms=run_params.get("negated_terms")
        )
        if temp_df.empty: return temp_df, constraint_failed, {}

        # 2. Brand
        cur_brand = run_params.get("brand")
        if cur_brand:
            temp_df = filter_brand(temp_df, cur_brand)
            if temp_df.empty: return temp_df, False, {}

        # 3. Analyze logic (run only on strict pass)
        report = {}
        if analyze:
            report = analyze_constraints(
                temp_df,
                feature_constraints=feature_constraints,
                hard_filters=run_params.get("hard_filters", {}),
                max_budget=run_params.get("max_budget"),
                min_budget=run_params.get("min_budget")
            )
            failed_feats = report["feature_constraints"]["failed_constraints"]
            if failed_feats:
                print("Relaxing feature constraints within pipeline:", failed_feats)
                feature_constraints = {k: v for k, v in feature_constraints.items() if k not in failed_feats}

        # 4. Hard Filters
        temp_df = apply_hard_filters(temp_df, run_params.get("hard_filters", {}))
        if temp_df.empty: return temp_df, False, report

        # 5. Budget 
        temp_df = filter_budget(temp_df, run_params.get("max_budget"), run_params.get("min_budget"))
        return temp_df, False, report

    # --- EXECUTE PIPELINE ---
    
    base_params = {
        "body_type": body_type,
        "powertrain": powertrain,
        "drive_sys": drive_sys,
        "brand": brand,
        "max_budget": max_budget,
        "min_budget": min_budget,
        "hard_filters": kwargs,
        "negated_terms": negated_terms
    }

    # PASS 1: Strict
    filtered_df, is_failed, constraint_report = apply_pipeline(base_params.copy(), analyze=True)
    
    # Safety Check: Ensure constraint_report is always a dict
    if constraint_report is None:
        constraint_report = {}

    if is_failed:
        print("[VIKOR RANKING ENGINE] Feature constraint terlalu ketat, mencoba relax...")
        return {"recommendations": [], "constraint_report": constraint_report}

    print("\nConstraint Report:")
    print(constraint_report)

    # RELAXATION STEPS
    RELAX_STEPS = []
    if brand:
        RELAX_STEPS.append({"type": "Brand diabaikan", "apply": lambda p: p.update({"brand": None})})
    if powertrain:
        RELAX_STEPS.append({"type": "Powertrain diabaikan", "apply": lambda p: p.update({"powertrain": None})})
    if max_budget:
        RELAX_STEPS.append({"type": "Saran Ekstra (Budget Naik 1.3x)", "apply": lambda p: p.update({"max_budget": int(p["max_budget"] * 1.3)})})

    relax_log = []
    current_params = base_params.copy()

    for step in RELAX_STEPS:
        if not filtered_df.empty: 
            break
            
        print(f"[VIKOR RANKING ENGINE] Menerapkan Relax Strategy: {step['type']}...")
        step["apply"](current_params)
        
        filtered_df, _, _ = apply_pipeline(current_params)
        relax_log.append(step["type"])
        
        if not filtered_df.empty:
            break
            
    if constraint_report is not None:
        constraint_report["relax_notes"] = relax_log

    if filtered_df.empty:
        print("[VIKOR RANKING ENGINE] Dataset tetap kosong setelah semua relax strategy dikerahkan.")
        return {"recommendations": [], "constraint_report": constraint_report}

    if not weight_dict:
        weight_dict = {}


    # ==================================================
    # VIKOR RANKING
    # ==================================================
    print(f"[VIKOR RANKING ENGINE] Memulai algoritma VIKOR dengan bobot {weight_dict}...")
    ranked = vikor_rank(filtered_df, weight_dict)

    ranked = validate_compromise_solution(ranked)

    result = ranked.head(top_n)

    # ==================================================
    # COMPUTING NORMALIZED WEIGHT FOR FRONTEND
    # ==================================================
    features_in_df = [c for c in VIKOR_CRITERIA if c in filtered_df.columns]
    weights_array = build_weight_vector(weight_dict, features_in_df)
    normalized_weights = dict(zip(features_in_df, weights_array))
    constraint_report["normalized_weights"] = normalized_weights
    constraint_report["final_filtered_n"] = len(filtered_df)
    constraint_report["total_cars"] = len(DF_CARS)

    # ==================================================
    # OUTPUT FORMAT
    # ==================================================

    # --- RENAMING & SELECTION ---
    HEADER_TO_FIELD_MAP = {
        "BODY TYPE": "BODY_TYPE",
        "HORSE POWER (HP)": "HORSE_POWER",
        "TORQUE (Nm)": "TORQUE",
        "GROUND CLEARANCE": "GROUND_CLEARANCE",
        "BATTERY (KWH)": "BATTERY"
    }
    
    # Rename columns to match Pydantic schema field names
    result = result.rename(columns=HEADER_TO_FIELD_MAP)

    cols = [
        "BRAND",
        "MODEL",
        "VARIAN",
        "HARGAOTR",
        "VIKOR_S",
        "VIKOR_R",
        "VIKOR_Q",
        "VIKOR_STATUS",
        "VIKOR_Q1",
        "VIKOR_Q2",
        "VIKOR_DQ",
        "VIKOR_IS_COMPROMISE",
        "INDEX_POWER",
        "INDEX_HANDLING",
        "INDEX_EFFICIENCY",
        "INDEX_SAFETY",
        "INDEX_DRIVER_COMFORT",
        "INDEX_PASSENGER_COMFORT",
        "INDEX_TECH",
        "INDEX_SPACE",
        "INDEX_OFFROAD",
        "INDEX_LUXURY",
        "INDEX_LIFECYCLE_SAFE",
        "INDEX_BRAND_STRENGTH",
        "INDEX_PRICE",

        "DRIVE_SYS",
        "POWERTRAIN",
        "BODY_TYPE",
        "FUEL",
        "CC",
        "IS_TURBO",
        "HORSE_POWER",
        "TORQUE",
        "TRANSMISSION",
        "SEAT",
        "GROUND_CLEARANCE",
        "LONG",
        "WIDTH",
        "HEIGHT",
        "WHEELBASE",
        "EV_RANGE_KM",
        "BATTERY",
        "AIRBAGS",
        "ABS",
        "EBD",
        "ESC",
        "TCS",
        "AEB",
        "ACC",
        "LKA",
        "RCTA",
        "LANE_CENTERING",
        "APPLE_CARPLAY",
        "ANDROID_AUTO",
        "WIRELESS_CHARGER",
        "SUNROOF",
        "POWER_TAILGATE",
        "ELECTRIC_SEAT",
        "VENTILATED_SEAT",
        "MASSAGE_SEAT",
        "CAMERA_360",
        "HEAD_UP_DISPLAY",
        "REAR_SEAT_ENTERTAINMENT",
        "LEATHER_SEAT",
        "AMBIENT_LIGHT",
        "PARKING_BRAKE",
    ]
    
    # Tambahkan semua kolom W_DIST yang dihasilkan VIKOR
    w_dist_cols = [c for c in result.columns if c.startswith("W_DIST_")]
    cols.extend(w_dist_cols)

    cols = [c for c in cols if c in result.columns]

    records = result[cols].to_dict(orient="records")

    # --- Formatting & Decoding Layer ---
    from app.data_formatter import format_car_records
    records = format_car_records(records, TRANSMISSION_DECODING, DRIVETRAIN_DECODING)

    # --- 4. NUMPY SANITIZATION (CRITICAL FOR JSON SERIALIZATION) ---
    # FastAPI's default JSON encoder cannot handle numpy.float64 objects.
    # We must explicitly convert them to standard Python floats/ints.
    def sanitize_dict(d):
        if not isinstance(d, dict): return d
        new_d = {}
        for k, v in d.items():
            if isinstance(v, dict):
                new_d[k] = sanitize_dict(v)
            elif isinstance(v, list):
                new_d[k] = [sanitize_dict(i) if isinstance(i, dict) else (float(i) if isinstance(i, (np.floating, np.float64)) else (int(i) if isinstance(i, (np.integer, np.int64)) else i)) for i in v]
            elif isinstance(v, (np.floating, np.float64, np.float32)):
                new_d[k] = float(v)
            elif isinstance(v, (np.integer, np.int64, np.int32)):
                new_d[k] = int(v)
            elif isinstance(v, np.bool_):
                new_d[k] = bool(v)
            elif pd.isna(v):
                new_d[k] = None
            else:
                new_d[k] = v
        return new_d

    if constraint_report:
        constraint_report = sanitize_dict(constraint_report)

    status_msg = ""
    if relax_log:
        status_msg = "Relaxed: " + ", ".join(relax_log)

    if status_msg:
        for r in records:
            r["VIKOR_STATUS"] = status_msg

    print("[VIKOR RANKING ENGINE] Selesai! Mengembalikan hasil dan constraint report.")
    print("==================================================")

    return {
        "recommendations": records,
        "constraint_report": constraint_report
    }


# ======================================================
# DEBUG API
# ======================================================

def get_feature_summary():
    return FEATURE_SUMMARY