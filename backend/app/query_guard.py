# backend/app/query_guard.py

import pandas as pd
from typing import Optional, Tuple, List
import re

from .feature_ontology import (
    BODY_TYPE_MAP, POWERTRAIN_MAP, DRIVETRAIN_MAP, 
    DRIVETRAIN_ENCODING, FEATURE_CONSTRAINT_MAP, BRAND_MAP
)

# ======================================================
# NLP BUDGET PARSER (MOVED FROM RASA CUSTOM ACTIONS)
# ======================================================

def parse_budget_strings(raw_budgets: List[str]) -> Tuple[Optional[int], Optional[int]]:
    """
    Mengubah array list string ("200 juta", "500-600jt") menjadi min_budget dan max_budget (integer).
    """
    if not raw_budgets:
        return None, None
        
    text = " ".join(raw_budgets).lower()
    
    # Normalisasi teks uang
    text = text.replace("jutaan", "jt")
    text = text.replace("juta", "jt")
    text = text.replace("miliar", "m")
    text = text.replace("milyar", "m")
    
    # Ekstrak angka float
    numbers = re.findall(r"\d+(?:\.\d+)?", text)
    if not numbers:
        return None, None
        
    numbers = [float(n) for n in numbers]
    multiplier = 1
    
    if "jt" in text:
        multiplier = 1_000_000
    elif "m" in text:
        multiplier = 1_000_000_000
        
    if len(numbers) == 1:
        value = int(numbers[0] * multiplier)
        if value >= 1_000_000_000:
            return max(0, value - 100_000_000), value + 150_000_000
        elif value <= 500_000_000:
            return max(0, value - 50_000_000), value + 100_000_000
        else:
            return max(0, value - 75_000_000), value + 125_000_000
            
    min_budget = int(numbers[0] * multiplier)
    max_budget = int(numbers[1] * multiplier)
    return min_budget, max_budget

# Body Type and Powertrain normalization uses maps from feature_ontology.py

def normalize_body_type(df: pd.DataFrame):
    df = df.copy()
    if "BODY TYPE" not in df.columns:
        return df
    df["BODY TYPE"] = df["BODY TYPE"].astype(str).str.lower()
    df["BODY_GROUP"] = df["BODY TYPE"].map(BODY_TYPE_MAP).fillna("OTHER")
    return df


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
# FILTER DRIVETRAIN
# ======================================================

def filter_drive_sys(df: pd.DataFrame, drive_sys=None):
    if drive_sys is None:
        return df
        
    if "DRIVE_SYS" not in df.columns:
        return df
        
    # Cocokkan drivetrain menggunakan encoding numerik (FWD=1, RWD=2, AWD=3, 4WD=4)
    target_code = DRIVETRAIN_ENCODING.get(drive_sys)
    if target_code is None:
        return df

    filtered = df[df["DRIVE_SYS"] == target_code]
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
# NEGATION FILTER
# ======================================================

def apply_negations(df: pd.DataFrame, negated_terms: List[str]):
    """
    Jika ada entitas negated, kita HARUS drop list mobilnya dari dataset (Hard Constraints Drop).
    Misal: "jangan ev", "jangan suv", "jangan toyota".
    HARUS dipanggil setelah normalize_body_type dan normalize_powertrain.
    """
    if not negated_terms:
        return df
        
    filtered = df.copy()
    
    for term in negated_terms:
        text = term.lower().strip()
        found_category = False
        
        # 1. Cek apabila Powertrain (gunakan kolom POWERTRAIN yang sudah dinormalisasi)
        if text in POWERTRAIN_MAP:
            target = POWERTRAIN_MAP[text]
            if "POWERTRAIN" in filtered.columns:
                before = len(filtered)
                filtered = filtered[filtered["POWERTRAIN"] != target]
                print(f"[QUERY GUARD] Negasi Powertrain '{text}' ({target}): {before} -> {len(filtered)} rows")
                found_category = True
            
        # 2. Cek apabila Body Type (gunakan kolom BODY_GROUP yang sudah dinormalisasi)
        if text in BODY_TYPE_MAP:
            target = BODY_TYPE_MAP[text]
            if "BODY_GROUP" in filtered.columns:
                before = len(filtered)
                filtered = filtered[filtered["BODY_GROUP"] != target]
                print(f"[QUERY GUARD] Negasi Body Type '{text}' ({target}): {before} -> {len(filtered)} rows")
                found_category = True
            
        # 3. Cek apabila Brand
        if text in BRAND_MAP:
            target = BRAND_MAP[text]
            if "BRAND" in filtered.columns:
                before = len(filtered)
                filtered = filtered[filtered["BRAND"].str.lower() != target.lower()]
                print(f"[QUERY GUARD] Negasi Brand '{text}' ({target}): {before} -> {len(filtered)} rows")
                found_category = True
            
        # 4. Cek apabila Drivetrain
        if text in DRIVETRAIN_MAP:
            label = DRIVETRAIN_MAP[text]
            target_code = DRIVETRAIN_ENCODING.get(label)
            if target_code and "DRIVE_SYS" in filtered.columns:
                before = len(filtered)
                filtered = filtered[filtered["DRIVE_SYS"] != target_code]
                print(f"[QUERY GUARD] Negasi Drivetrain '{text}' ({label}/{target_code}): {before} -> {len(filtered)} rows")
                found_category = True
            
        # 5. Cek apabila Feature boolean
        if text in FEATURE_CONSTRAINT_MAP:
            col, val = FEATURE_CONSTRAINT_MAP[text]
            if col in filtered.columns:
                before = len(filtered)
                filtered = filtered[filtered[col] < val]
                print(f"[QUERY GUARD] Negasi Feature '{text}' ({col}<{val}): {before} -> {len(filtered)} rows")
                found_category = True

        # 6. Fallback: Substring match terhadap Brand/Model (Jika tidak masuk kategori manapun)
        if not found_category:
            before = len(filtered)
            # Buat filter substring: MODEL atau BRAND tidak boleh mengandung term negasi
            if "MODEL" in filtered.columns and "BRAND" in filtered.columns:
                mask = ~(
                    filtered["MODEL"].str.lower().str.contains(text, na=False) | 
                    filtered["BRAND"].str.lower().str.contains(text, na=False)
                )
                filtered = filtered[mask]
                if len(filtered) < before:
                    print(f"[QUERY GUARD] Negasi Nama/Model '{text}': {before} -> {len(filtered)} rows (Substring Match)")
                    found_category = True

        if not found_category:
            print(f"[QUERY GUARD] Term negasi '{text}' tidak dikenali dalam ontologi maupun nama mobil, diabaikan.")
            
    return filtered



# ======================================================
# MAIN QUERY GUARD
# ======================================================

def apply_query_guard(df: pd.DataFrame,
                     body_type=None,
                     powertrain=None,
                     drive_sys=None,
                     feature_constraints=None,
                     negated_terms=None):

    """
    Pipeline proteksi sebelum ranking:
    1. Normalisasi kolom (POWERTRAIN, BODY_GROUP)
    2. Terapkan negasi (exclusion mutlak)
    3. Filter positif (body, powertrain, drivetrain, features)
    """
    # Step 1: Normalisasi dulu supaya kolom POWERTRAIN dan BODY_GROUP tersedia
    df = normalize_body_type(df)
    df = normalize_powertrain(df)

    # Step 2: Terapkan negasi SETELAH normalisasi
    if negated_terms:
        df = apply_negations(df, negated_terms)

    # Step 3: Filter positif
    df = filter_body_type(df, body_type)
    df = filter_powertrain(df, powertrain)
    df = filter_drive_sys(df, drive_sys)

    df, constraint_failed = validate_feature_constraints(
        df,
        feature_constraints
    )

    return df, constraint_failed