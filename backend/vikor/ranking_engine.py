# backend/vikor/ranking_engine.py

import os
import sys
import pandas as pd

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
from clustering.agglomerative import perform_clustering

from app.query_guard import apply_query_guard
from app.feature_inspector import generate_feature_summary
from app.constraint_analyzer import analyze_constraints
from .vikor import vikor_rank, validate_compromise_solution, build_weight_vector, VIKOR_CRITERIA
from app.feature_ontology import DRIVETRAIN_DECODING



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

    df = perform_clustering(df)

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

    if req_kwargs.get("min_ground_clearance") is not None:
        df = df[df["GROUND CLEARANCE"] >= req_kwargs["min_ground_clearance"]]

    if req_kwargs.get("must_have_sunroof"):
        df = df[df["SUNROOF"] > 0]

    if req_kwargs.get("must_have_wireless_tech"):
        df = df[(df["APPLE_CARPLAY"] == 2) | (df["ANDROID_AUTO"] == 2)]

    return df


# ======================================================
# MAIN RECOMMENDATION ENGINE
# ======================================================

def recommend_cars(
    weight_dict=None,
    cluster_name=None,
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
        if temp_df.empty: return temp_df, constraint_failed, None

        # 2. Brand
        cur_brand = run_params.get("brand")
        if cur_brand:
            temp_df = filter_brand(temp_df, cur_brand)
            if temp_df.empty: return temp_df, False, None

        # 3. Analyze logic (run only on strict pass)
        report = None
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
            
    constraint_report["relax_notes"] = relax_log

    if filtered_df.empty:
        print("[VIKOR RANKING ENGINE] Dataset tetap kosong setelah semua relax strategy dikerahkan.")
        return {"recommendations": [], "constraint_report": constraint_report}

    # ==================================================
    # CLUSTER SOFT CONSTRAINT (BOOSTING)
    # ==================================================

    filtered_df["INDEX_CLUSTER_MATCH"] = 0.0

    if cluster_name:
        filtered_df["CLUSTER_SCORE"] = (filtered_df["CLUSTER_NAME"] == cluster_name).astype(int)
        filtered_df["INDEX_CLUSTER_MATCH"] = filtered_df["CLUSTER_SCORE"] * 0.2

        # Tambahkan bobot prioritas ke cluster filter agar VIKOR mempertimbangkannya
        if "INDEX_CLUSTER_MATCH" not in weight_dict:
            weight_dict["INDEX_CLUSTER_MATCH"] = 1.0  # Bobot yang cukup besar agar ranking naik

        print(f"[VIKOR RANKING ENGINE] Soft Constraint Cluster '{cluster_name}' diterapkan (boost).")

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

    cols = [
        "BRAND",
        "MODEL",
        "VARIAN",
        "HARGAOTR",
        "CLUSTER_NAME",
        "VIKOR_S",
        "VIKOR_R",
        "VIKOR_Q",
        "VIKOR_Q1",
        "VIKOR_Q2",
        "VIKOR_DQ",
        "VIKOR_IS_COMPROMISE",
        "VIKOR_STATUS",
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
        "INDEX_PARTS_AVAILABILITY",   # Ketersediaan spare parts & jaringan dealer
        "INDEX_MARKET_DEMAND",        # Popularitas & permintaan pasar aktual
        "INDEX_PRICE",
        "INDEX_CLUSTER_MATCH",
        "DRIVE_SYS",
        "POWERTRAIN"
    ]

    cols = [c for c in cols if c in result.columns]

    records = result[cols].to_dict(orient="records")

    # Decode numeric features for front-end visibility (fixing float vs string schema error)
    for r in records:
        if r.get("DRIVE_SYS") is not None:
            val = r["DRIVE_SYS"]
            try:
                r["DRIVE_SYS"] = DRIVETRAIN_DECODING.get(float(val), f"CODE_{val}")
            except:
                r["DRIVE_SYS"] = str(val)
        
        if r.get("POWERTRAIN") is not None:
             r["POWERTRAIN"] = str(r["POWERTRAIN"])


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