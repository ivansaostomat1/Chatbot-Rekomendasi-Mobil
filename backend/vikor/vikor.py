# chatbot-rekomendasi-mobil/backend/vikor/vikor.py

import numpy as np
import pandas as pd


# ======================================================
# CRITERIA YANG DIGUNAKAN VIKOR
# ======================================================

VIKOR_CRITERIA = [
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
    "INDEX_LIFECYCLE_SAFE",       # Ketersediaan spare parts & jaringan dealer (dari wholesale)
    "INDEX_BRAND_STRENGTH",       # Popularitas & permintaan pasar aktual (dari retail)
    "INDEX_PRICE",
    "INDEX_CLUSTER_MATCH"         # <-- soft constraint boosting
]


# ======================================================
# HELPER: BUILD WEIGHT VECTOR
# ======================================================

def build_weight_vector(weight_dict, criteria):

    # Jika user tidak memberikan kriteria spesifik sama sekali (dict kosong)
    # Berikan equal weight (dibagi rata ke semua kriteria)
    if not weight_dict:
        return np.ones(len(criteria)) / len(criteria)

    weights = []

    for c in criteria:
        # Default ke 0.0 jika tidak disebut oleh NLP
        weights.append(weight_dict.get(c, 0.0))

    weights = np.array(weights, dtype=float)

    # Jaga-jaga jika semua bobot NLP tidak valid / jumlahnya 0
    if weights.sum() == 0:
        weights = np.ones(len(criteria))

    # Normalisasi agar total bobot selalu 1.0 (100%)
    weights = weights / weights.sum()

    return weights

# ======================================================
# MAIN VIKOR FUNCTION
# ======================================================

def vikor_rank(df, weight_dict=None, v=0.5):

    features = [c for c in VIKOR_CRITERIA if c in df.columns]

    # PERBAIKAN INDENTASI
    if not (0 <= v <= 1):
        raise ValueError("Parameter v harus antara 0 dan 1")
    
    if len(features) == 0:
        raise ValueError("Tidak ada kriteria VIKOR ditemukan")

    # ==================================================
    # DECISION MATRIX
    # ==================================================

    matrix = df[features].values.astype(float)

    # ==================================================
    # BEST & WORST VALUES
    # ==================================================

    f_star = matrix.max(axis=0)
    f_minus = matrix.min(axis=0)

    # ==================================================
    # WEIGHTS
    # ==================================================

    if weight_dict is None:
        weight_dict = {}

    weights = build_weight_vector(weight_dict, features)

    # ==================================================
    # VIKOR DISTANCE MATRIX (Vectorized)
    # ==================================================

    denom = (f_star - f_minus)
    denom[denom == 0] = 1e-9

    D = (f_star - matrix) / denom

    # ==================================================
    # S (GROUP UTILITY) & R (INDIVIDUAL REGRET)
    # ==================================================

    S = np.sum(weights * D, axis=1)
    R = np.max(weights * D, axis=1)

    # ==================================================
    # NORMALIZATION OF S AND R
    # ==================================================

    S_star = S.min()
    S_minus = S.max()

    R_star = R.min()
    R_minus = R.max()

    denom_S = (S_minus - S_star)
    denom_R = (R_minus - R_star)

    if denom_S == 0:
        denom_S = 1e-9

    if denom_R == 0:
        denom_R = 1e-9

    # ==================================================
    # Q (VIKOR INDEX)
    # ==================================================

    Q = v * (S - S_star) / denom_S + (1 - v) * (R - R_star) / denom_R

    # ==================================================
    # ATTACH RESULTS
    # ==================================================

    result = df.copy()

    result["VIKOR_S"] = S
    result["VIKOR_R"] = R
    result["VIKOR_Q"] = Q

    result = result.sort_values("VIKOR_Q")

    return result

# ======================================================
# COMPROMISE SOLUTION VALIDATION (PENDEKATAN B / UX)
# ======================================================

def validate_compromise_solution(df):

    df = df.sort_values("VIKOR_Q").reset_index(drop=True)
    m = len(df)

    # 1. Berikan label default untuk semua alternatif di bawah juara
    df["VIKOR_STATUS"] = "Alternatif Lain"

    if m < 2:
        if m == 1:
            df.loc[0, "VIKOR_STATUS"] = "Pemenang Mutlak ⭐"
        return df

    Q1 = df.loc[0, "VIKOR_Q"]
    Q2 = df.loc[1, "VIKOR_Q"]
    DQ = 1 / (m - 1)

    condition1 = (Q2 - Q1) >= DQ
    best_S = df["VIKOR_S"].idxmin()
    best_R = df["VIKOR_R"].idxmin()
    condition2 = (best_S == 0) or (best_R == 0)

    # --------------------------------------------------
    # EVALUASI KOMPROMI & TAGGING
    # --------------------------------------------------

    if condition1 and condition2:
        # Menang mutlak (Cuma peringkat 1 yang dapat bintang)
        df.loc[0, "VIKOR_STATUS"] = "Pemenang Mutlak ⭐"
        df["VIKOR_IS_COMPROMISE"] = False

    elif not condition1:
        # Kompromi (Peringkat 1, 2, dst yang masuk threshold dapat bintang)
        threshold = Q1 + DQ
        compromise_idx = df.index[df["VIKOR_Q"] <= threshold].tolist()
        df.loc[compromise_idx, "VIKOR_STATUS"] = "Rekomendasi Setara ⭐"
        df["VIKOR_IS_COMPROMISE"] = True

    else:
        # Kompromi (Hanya Peringkat 1 dan 2 yang dapat bintang)
        df.loc[[0, 1], "VIKOR_STATUS"] = "Rekomendasi Setara ⭐"
        df["VIKOR_IS_COMPROMISE"] = True

    df["VIKOR_Q1"] = Q1
    df["VIKOR_Q2"] = Q2
    df["VIKOR_DQ"] = DQ

    # 2. Kembalikan SELURUH dataframe, jangan dipotong!
    return df
    print(df[["MODEL","HARGAOTR","INDEX_PRICE"]].sort_values("INDEX_PRICE",ascending=False).head())