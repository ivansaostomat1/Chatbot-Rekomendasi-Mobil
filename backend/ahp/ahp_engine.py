# backend/ahp/ahp_engine.py
#
# ANALYTIC HIERARCHY PROCESS (AHP) ENGINE
# ---------------------------------------------------------------------------
# Modul ini menggantikan HAC (Hierarchical Agglomerative Clustering).
#
# PERAN:
#   HAC sebelumnya mengelompokkan mobil ke dalam cluster, lalu memberikan
#   skor flat (+0.2) ke mobil yang clusternya cocok dengan preferensi user.
#
#   AHP menggantikan peran ini dengan cara yang jauh lebih presisi:
#   1. Mengambil preferensi user dari NLU (misal: "irit", "nyaman", "aman")
#   2. Mengubah preferensi tersebut menjadi matriks pairwise comparison
#   3. Menghitung bobot prioritas menggunakan eigenvector method
#   4. Memvalidasi konsistensi logika user (Consistency Ratio < 0.1)
#   5. Menyuntikkan bobot yang sudah tervalidasi ke VIKOR
#
# REFERENSI:
#   Saaty, T.L. (1980). The Analytic Hierarchy Process. McGraw-Hill.
# ---------------------------------------------------------------------------

import numpy as np
from typing import Dict, List, Tuple, Optional

# ======================================================
# SKALA SAATY (1-9)
# ======================================================
# 1 = Sama penting
# 3 = Sedikit lebih penting
# 5 = Cukup lebih penting
# 7 = Sangat lebih penting
# 9 = Mutlak lebih penting
# 2,4,6,8 = Nilai antara (kompromi)

# ======================================================
# RANDOM INDEX (RI) SAATY
# Digunakan untuk menghitung Consistency Ratio (CR)
# ======================================================
RANDOM_INDEX = {
    1: 0.00,
    2: 0.00,
    3: 0.58,
    4: 0.90,
    5: 1.12,
    6: 1.24,
    7: 1.32,
    8: 1.41,
    9: 1.45,
    10: 1.49,
    11: 1.51,
    12: 1.48,
    13: 1.56,
    14: 1.57,
    15: 1.59,
}

# ======================================================
# KRITERIA AHP (Konsisten dengan VIKOR_CRITERIA)
# ======================================================
AHP_CRITERIA = [
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
]


# ======================================================
# CORE AHP: CALCULATE WEIGHTS FROM PAIRWISE MATRIX
# ======================================================


def calculate_ahp_weights(
    pairwise_matrix: np.ndarray,
) -> Tuple[np.ndarray, float, bool]:
    """
    Menghitung bobot prioritas dari matriks perbandingan berpasangan
    menggunakan metode eigenvector (pendekatan geometrik mean).

    Parameters:
        pairwise_matrix: Matriks n x n perbandingan berpasangan (Skala Saaty)

    Returns:
        (weights, CR, is_consistent)
        - weights: Array bobot ternormalisasi (sum = 1.0)
        - CR: Consistency Ratio
        - is_consistent: True jika CR < 0.1
    """
    n = pairwise_matrix.shape[0]

    if n == 0:
        return np.array([]), 0.0, True

    # ──────────────────────────────────────────────
    # STEP 1: Geometric Mean Method (lebih stabil dari power method)
    # Untuk setiap baris, hitung geometric mean
    # ──────────────────────────────────────────────
    geo_means = np.prod(pairwise_matrix, axis=1) ** (1.0 / n)

    # Normalisasi geometric mean menjadi bobot (sum = 1)
    weights = geo_means / geo_means.sum()

    # ──────────────────────────────────────────────
    # STEP 2: Hitung Consistency Index (CI)
    # CI = (lambda_max - n) / (n - 1)
    # ──────────────────────────────────────────────

    # Hitung lambda_max: eigenvalue terbesar
    # A * w = lambda_max * w
    Aw = pairwise_matrix @ weights
    lambda_max = np.mean(Aw / weights)

    if n <= 2:
        # Matriks 1x1 atau 2x2 selalu konsisten
        return weights, 0.0, True

    CI = (lambda_max - n) / (n - 1)

    # ──────────────────────────────────────────────
    # STEP 3: Hitung Consistency Ratio (CR)
    # CR = CI / RI
    # CR < 0.1 → Konsisten (acceptable)
    # ──────────────────────────────────────────────
    RI = RANDOM_INDEX.get(n, 1.56)

    if RI == 0:
        CR = 0.0
    else:
        CR = CI / RI

    is_consistent = CR < 0.1

    return weights, float(CR), is_consistent


# ======================================================
# CONVERT PREFERENCE WEIGHTS → PAIRWISE MATRIX
# ======================================================


def build_pairwise_from_weights(weight_profile: Dict[str, float]) -> np.ndarray:
    """
    Mengonversi profil bobot (skala 0-10) menjadi matriks pairwise comparison
    pada Skala Saaty (1-9).

    Logika konversi:
    - Jika bobot kriteria A = 8 dan B = 4, maka rasio A/B = 2.0
    - Rasio ini di-map ke Skala Saaty:
      - Rasio 1.0 → Saaty 1 (sama penting)
      - Rasio 2.0 → Saaty 3 (sedikit lebih penting)
      - Rasio 3.0 → Saaty 5 (cukup lebih penting)
      - Rasio 4.0+ → Saaty 7 (sangat lebih penting)
      - Rasio 5.0+ → Saaty 9 (mutlak lebih penting)

    Parameters:
        weight_profile: Dict {INDEX_*: bobot (0-10)} dari preference_weight_map

    Returns:
        Matriks n x n pairwise comparison (Skala Saaty)
    """
    n = len(AHP_CRITERIA)
    matrix = np.ones((n, n))

    # Ambil bobot untuk setiap kriteria, default 5.0 (netral)
    raw_weights = []
    for c in AHP_CRITERIA:
        raw_weights.append(
            max(weight_profile.get(c, 5.0), 0.5)
        )  # min 0.5 untuk hindari div/0

    for i in range(n):
        for j in range(i + 1, n):
            ratio = raw_weights[i] / raw_weights[j]

            # Map rasio ke Skala Saaty
            saaty_val = _ratio_to_saaty(ratio)

            matrix[i][j] = saaty_val
            matrix[j][i] = 1.0 / saaty_val  # Resiprositas: a_ji = 1/a_ij

    return matrix


def _ratio_to_saaty(ratio: float) -> float:
    """
    Mengonversi rasio bobot ke Skala Saaty (1-9).
    Menggunakan mapping linear yang halus.
    """
    if ratio >= 1.0:
        # Kriteria i lebih penting dari j
        if ratio <= 1.2:
            return 1.0  # Sama penting
        elif ratio <= 1.5:
            return 2.0  # Antara sama dan sedikit lebih penting
        elif ratio <= 2.0:
            return 3.0  # Sedikit lebih penting
        elif ratio <= 2.5:
            return 4.0  # Antara sedikit dan cukup lebih penting
        elif ratio <= 3.0:
            return 5.0  # Cukup lebih penting
        elif ratio <= 4.0:
            return 6.0  # Antara cukup dan sangat lebih penting
        elif ratio <= 5.0:
            return 7.0  # Sangat lebih penting
        elif ratio <= 7.0:
            return 8.0  # Antara sangat dan mutlak lebih penting
        else:
            return 9.0  # Mutlak lebih penting
    else:
        # Kebalikan: j lebih penting dari i
        # Dikembalikan sebagai desimal (akan di-reciprocal di caller)
        return 1.0 / _ratio_to_saaty(1.0 / ratio)


# ======================================================
# MAIN ENTRY POINT: GET AHP WEIGHTS
# ======================================================


def get_ahp_weights(
    preference_weights: Dict[str, float], profile_name: str = "Dynamic"
) -> Dict[str, any]:
    """
    Entry point utama modul AHP.
    Menerima bobot preferensi dari NLU/preference_weight_map,
    mengonversinya ke matriks pairwise, lalu menghitung bobot AHP.

    Parameters:
        preference_weights: Dict {INDEX_*: bobot (0-10)} dari resolve_preference_weights()
        profile_name: Nama profil untuk logging

    Returns:
        Dict berisi:
        - ahp_weights: Dict {INDEX_*: normalized_weight}
        - consistency_ratio: Float CR value
        - is_consistent: Boolean
        - pairwise_matrix: List[List[float]] untuk debugging/evaluasi
        - profile_name: String nama profil
    """
    print(f"")
    print(f"[AHP] ===================================================")
    print(f"[AHP] Memulai kalkulasi AHP untuk profil: '{profile_name}'")
    print(f"[AHP] Input weights: {preference_weights}")

    # Step 1: Konversi ke matriks pairwise
    pairwise = build_pairwise_from_weights(preference_weights)

    # Step 2: Hitung bobot AHP
    weights, CR, is_consistent = calculate_ahp_weights(pairwise)

    # Step 3: Map kembali ke nama kriteria
    ahp_weight_dict = {}
    for i, criteria in enumerate(AHP_CRITERIA):
        ahp_weight_dict[criteria] = round(float(weights[i]), 6)

    # Logging
    print(
        f"[AHP] Consistency Ratio (CR): {CR:.4f} {'[OK] KONSISTEN' if is_consistent else '[X] TIDAK KONSISTEN'}"
    )
    print(f"[AHP] Threshold: CR < 0.10")

    print(f"[AHP] Bobot AHP yang dihasilkan:")
    # Sort by weight descending for readability
    sorted_weights = sorted(ahp_weight_dict.items(), key=lambda x: x[1], reverse=True)
    for criteria, weight in sorted_weights:
        bar = "#" * int(weight * 100)
        print(f"[AHP]   {criteria:30s} = {weight:.4f} {bar}")

    print(f"[AHP] ===================================================")

    return {
        "ahp_weights": ahp_weight_dict,
        "consistency_ratio": round(CR, 4),
        "is_consistent": is_consistent,
        "pairwise_matrix": pairwise.tolist(),
        "profile_name": profile_name,
    }


# ======================================================
# EVALUASI: Hitung AHP untuk semua profil statis
# ======================================================


def evaluate_all_profiles(profiles: Dict[str, Dict[str, float]]) -> Dict[str, any]:
    """
    Menghitung AHP untuk seluruh profil yang didefinisikan di feature_ontology.
    Digunakan oleh endpoint /evaluasi/ahp.

    Parameters:
        profiles: Dict {profile_name: {short_key: weight_value}}
                  Contoh: {"Urban Agility": {"power": 5, "handling": 6, ...}}

    Returns:
        Dict berisi hasil AHP untuk setiap profil
    """
    from app.feature_ontology import UI_TO_INDEX_MAP

    results = {}

    for profile_name, short_weights in profiles.items():
        # Konversi short keys ke INDEX_ keys
        index_weights = {}
        for short_key, val in short_weights.items():
            index_key = UI_TO_INDEX_MAP.get(short_key, short_key)
            index_weights[index_key] = float(val)

        result = get_ahp_weights(index_weights, profile_name=profile_name)
        results[profile_name] = result

    return results
