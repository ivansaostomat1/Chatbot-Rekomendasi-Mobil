# backend/app/feature_engineering/preference_weight_map.py
#
# PETA PREFERENSI --- BOBOT VIKOR
# ---------------------------------------------------------------------------
# File ini menjadi satu-satunya sumber kebenaran (single source of truth)
# untuk translasi preferensi user (bahasa natural) ke bobot kriteria VIKOR.
#
# STRUKTUR:
#   Setiap key  = kata/frasa preferensi (lowercase, setelah .strip().lower())
#   Setiap value = dict {nama_kriteria: bobot (0-10)}
#
# KRITERIA YANG TERSEDIA (harus konsisten dengan scoring.py):
#   power           --- Tenaga & Akselerasi         (INDEX_POWER)
#   handling        --- Stabilitas & Kelincahan      (INDEX_HANDLING)
#   efficiency      --- Efisiensi BBM               (INDEX_EFFICIENCY)
#   driver_comfort  --- Kenyamanan Pengemudi         (INDEX_DRIVER_COMFORT)
#   passenger_comfort --- Kenyamanan Penumpang       (INDEX_PASSENGER_COMFORT)
#   safety          --- Fitur Keamanan              (INDEX_SAFETY)
#   tech            --- Teknologi & Fitur Modern    (INDEX_TECH)
#   space           --- Keluasan Kabin & Bagasi     (INDEX_SPACE)
#   offroad         --- Keandalan Jalan Rusak       (INDEX_OFFROAD)
#   luxury          --- Kesan Mewah & Premium       (INDEX_LUXURY)
#   lifecycle       --- Model Aman (Anti-Discontinue)(INDEX_LIFECYCLE_SAFE)
#   brand_strength  --- Reputasi & Jaringan Merek   (INDEX_BRAND_STRENGTH)
#   price           --- Value for Money             (INDEX_PRICE)
#
# SKALA BOBOT:
#   9-10 = Sangat dominan / inti dari preferensi ini
#   7-8  = Kontribusi kuat
#   5-6  = Kontribusi sedang (sering muncul bersama preferensi utama)
#   3-4  = Kontribusi lemah / implisit
#   0-2  = Tidak relevan (tidak perlu ditulis, akan default ke 5)
# ---------------------------------------------------------------------------

import numpy as np
from numpy.linalg import norm
from typing import Dict, List
from .semantic_mapper import get_mapper
from ..feature_ontology import GLOBAL_DEFAULT_PROFILE, CLUSTER_PROFILES

# ======================================================
# KAMUS UTAMA: PREFERENSI --- BOBOT MULTI-KRITERIA
# ======================================================

PREFERENCE_WEIGHT_MAP: Dict[str, Dict[str, float]] = {

    # --------- EFISIENSI / IRIT -------------------------------------------------
    "irit": {
        "efficiency": 10,
        "price": 7,
    },
    "hemat": {
        "efficiency": 10,
        "price": 7,
    },
    "hemat bbm": {
        "efficiency": 10,
        "price": 6,
    },
    "bbm": {
        "efficiency": 9,
    },
    "konsumsi bbm": {
        "efficiency": 9,
    },
    "ekonomis": {
        "efficiency": 9,
        "price": 7,
    },
    "efisien": {
        "efficiency": 9,
        "price": 6,
    },

    # --------- PERFORMA / KENCANG -----------------------------------------------
    "kencang": {
        "power": 10,
        "handling": 5,
    },
    "ngebut": {
        "power": 10,
        "handling": 6,
    },
    "lari": {
        "power": 9,
        "handling": 5,
    },
    "performa": {
        "power": 9,
        "handling": 6,
    },
    "bertenaga": {
        "power": 10,
        "handling": 4,
    },
    "tarikan kuat": {
        "power": 9,
        "handling": 4,
    },
    "tarikan": {
        "power": 8,
    },
    "akselerasi": {
        "power": 9,
        "handling": 5,
    },
    "responsif": {
        "power": 7,
        "handling": 8,
    },
    "sporty": {
        "power": 8,
        "handling": 9,
    },
    "sport": {
        "power": 8,
        "handling": 8,
    },
    "fun": {
        "power": 7,
        "handling": 8,
    },
    "enak dikendarai": {
        "driver_comfort": 8,
        "handling": 7,
    },

    # --------- HANDLING / KELINCAHAN --------------------------------------------
    "lincah": {
        "handling": 10,
        "power": 5,
    },
    "gesit": {
        "handling": 10,
        "power": 5,
    },
    "handling": {
        "handling": 10,
    },
    "stabil": {
        "handling": 9,
    },
    "stabilitas": {
        "handling": 9,
    },
    "handlingnya mantap": {
        "handling": 10,
    },
    "selap-selip": {
        "handling": 9,
        "power": 4,
    },
    "lincah dan gesit": {
        "handling": 10,
        "power": 5,
    },

    # --------- KENYAMANAN -------------------------------------------------------
    "nyaman": {
        "driver_comfort": 8,
        "passenger_comfort": 8,
    },
    "kenyamanan": {
        "driver_comfort": 8,
        "passenger_comfort": 8,
    },
    "empuk": {
        "driver_comfort": 8,
        "passenger_comfort": 8,
    },
    "senyap": {
        "driver_comfort": 7,
        "passenger_comfort": 7,
        "luxury": 5,
    },
    "santai": {
        "driver_comfort": 7,
        "passenger_comfort": 7,
    },
    "premium feel": {
        "driver_comfort": 7,
        "passenger_comfort": 7,
        "luxury": 7,
    },

    # --------- PENGGUNAAN HARIAN ------------------------------------------------
    "harian": {
        "efficiency": 8,
        "driver_comfort": 8,
        "price": 7,
        "brand_strength": 5,
    },
    "daily": {
        "efficiency": 8,
        "driver_comfort": 8,
        "price": 7,
        "brand_strength": 5,
    },
    "daily driver": {
        "efficiency": 8,
        "driver_comfort": 8,
        "price": 7,
        "brand_strength": 5,
    },
    "kantor": {
        "driver_comfort": 8,
        "efficiency": 7,
        "price": 6,
    },
    "kerja": {
        "driver_comfort": 7,
        "efficiency": 7,
        "price": 6,
    },
    "enak buat harian": {
        "efficiency": 8,
        "driver_comfort": 8,
        "price": 7,
    },

    # --------- PERJALANAN JAUH / MUDIK ------------------------------------------
    "perjalanan jauh": {
        "driver_comfort": 9,
        "passenger_comfort": 8,
        "efficiency": 7,
        "safety": 6,
    },
    "mudik": {
        "driver_comfort": 8,
        "passenger_comfort": 8,
        "efficiency": 7,
        "space": 6,
        "safety": 6,
    },
    "touring": {
        "driver_comfort": 8,
        "efficiency": 7,
        "power": 5,
    },
    "long trip": {
        "driver_comfort": 9,
        "passenger_comfort": 8,
        "efficiency": 7,
    },

    # --------- KELUARGA ---------------------------------------------------------
    "keluarga": {
        "space": 9,
        "passenger_comfort": 8,
        "safety": 7,
        "efficiency": 5,
    },
    "keluarga besar": {
        "space": 10,
        "passenger_comfort": 9,
        "safety": 7,
    },
    "untuk keluarga": {
        "space": 9,
        "passenger_comfort": 8,
        "safety": 7,
    },
    "buat keluarga": {
        "space": 9,
        "passenger_comfort": 8,
        "safety": 7,
    },
    "family": {
        "space": 9,
        "passenger_comfort": 8,
        "safety": 7,
    },

    # --------- RUANG KABIN ------------------------------------------------------
    "luas": {
        "space": 10,
        "passenger_comfort": 6,
    },
    "kabin luas": {
        "space": 10,
        "passenger_comfort": 7,
    },
    "lega": {
        "space": 9,
        "passenger_comfort": 6,
    },
    "banyak kursi": {
        "space": 9,
        "passenger_comfort": 7,
    },

    # --------- KEAMANAN ---------------------------------------------------------
    "aman": {
        "safety": 10,
    },
    "safety": {
        "safety": 10,
    },
    "keamanan": {
        "safety": 10,
    },
    "adas": {
        "safety": 9,
        "tech": 6,
    },
    "airbag": {
        "safety": 9,
    },

    # --------- TEKNOLOGI / FITUR ------------------------------------------------
    "teknologi": {
        "tech": 10,
        "luxury": 4,
    },
    "fitur": {
        "tech": 9,
    },
    "canggih": {
        "tech": 9,
        "luxury": 5,
    },
    "modern": {
        "tech": 8,
        "luxury": 5,
    },
    "fitur lengkap": {
        "tech": 9,
        "safety": 5,
    },
    "fitur canggih": {
        "tech": 10,
        "luxury": 5,
    },
    "teknologi canggih": {
        "tech": 10,
        "luxury": 5,
    },
    "hi-tech": {
        "tech": 10,
    },

    # --------- MEWAH / PREMIUM --------------------------------------------------
    "mewah": {
        "luxury": 10,
        "driver_comfort": 7,
        "passenger_comfort": 7,
    },
    "luxury": {
        "luxury": 10,
        "driver_comfort": 7,
        "passenger_comfort": 7,
    },
    "premium": {
        "luxury": 9,
        "driver_comfort": 6,
        "passenger_comfort": 6,
    },
    "elegan": {
        "luxury": 8,
        "driver_comfort": 6,
    },
    "prestige": {
        "luxury": 9,
        "brand_strength": 6,
    },

    # --------- OFFROAD / TANGGUH ------------------------------------------------
    "tangguh": {
        "offroad": 9,
        "power": 6,
    },
    "offroad": {
        "offroad": 10,
        "power": 6,
    },
    "banjir": {
        "offroad": 10,
    },
    "bebas banjir": {
        "offroad": 10,
    },
    "trabas banjir": {
        "offroad": 10,
    },
    "jalan rusak": {
        "offroad": 9,
    },
    "nanjak": {
        "offroad": 9,
        "power": 7,
    },
    "medan berat": {
        "offroad": 10,
        "power": 7,
    },
    "disegala medan": {
        "offroad": 10,
        "power": 6,
    },
    "ground clearance tinggi": {
        "offroad": 9,
    },

    # --------- AFTER SALES / PERAWATAN ------------------------------------------
    "sparepart gampang": {
        "brand_strength": 9,
        "lifecycle": 6,
    },
    "bengkel banyak": {
        "brand_strength": 10,
    },
    "aftersales": {
        "brand_strength": 9,
    },
    "perawatan mudah": {
        "brand_strength": 8,
        "lifecycle": 6,
    },
    "onderdil": {
        "brand_strength": 8,
        "lifecycle": 6,
    },
    "servis mudah": {
        "brand_strength": 8,
    },
    "biaya perawatan murah": {
        "brand_strength": 7,
        "price": 7,
    },

    # --------- REPUTASI / POPULARITAS -------------------------------------------
    "paling laku": {
        "brand_strength": 9,
        "lifecycle": 6,
    },
    "populer": {
        "brand_strength": 8,
        "lifecycle": 6,
    },
    "laris": {
        "brand_strength": 8,
        "lifecycle": 6,
    },
    "terpercaya": {
        "brand_strength": 8,
    },
    "reputasi bagus": {
        "brand_strength": 8,
    },

    # --------- NILAI JUAL KEMBALI -----------------------------------------------
    "harga bekas": {
        "brand_strength": 7,
        "lifecycle": 9,
    },
    "nilai jual": {
        "brand_strength": 7,
        "lifecycle": 8,
    },
    "resale value": {
        "brand_strength": 7,
        "lifecycle": 9,
    },

    # --------- SEGMEN ANAK MUDA / KULIAH ----------------------------------------
    "anak muda": {
        "price": 8,
        "tech": 7,
        "efficiency": 6,
        "handling": 5,
    },
    "kuliah": {
        "price": 9,
        "efficiency": 7,
        "tech": 6,
    },
    "pemuda": {
        "price": 7,
        "tech": 7,
        "handling": 6,
    },
    "fresh graduate": {
        "price": 8,
        "efficiency": 7,
        "tech": 6,
    },

    # --------- MOBIL KEDUA / PEMULA ---------------------------------------------
    "mobil kedua": {
        "price": 8,
        "efficiency": 7,
        "brand_strength": 5,
    },
    "pemula": {
        "safety": 8,
        "brand_strength": 7,
        "price": 6,
        "driver_comfort": 5,
    },
    "baru beli": {
        "safety": 7,
        "brand_strength": 7,
        "price": 6,
    },

    # --------- VALUE FOR MONEY --------------------------------------------------
    "worth it": {
        "price": 9,
        "tech": 5,
        "safety": 5,
    },
    "paling worth": {
        "price": 10,
        "tech": 5,
    },
    "value": {
        "price": 8,
    },
    "murah": {
        "price": 10,
    },
    "terjangkau": {
        "price": 9,
    },
    "budget": {
        "price": 8,
        "efficiency": 5,
    },
    "bagus": {
        "price": 6,
        "tech": 5,
        "driver_comfort": 5,
        "safety": 5,
    },
}

# ======================================================
# STOPWORDS: kata yang TIDAK boleh jadi entitas
# ======================================================
PREFERENCE_STOPWORDS = {
    "sedang", "saya", "mau", "ingin", "cari", "cariin", "carikan", "butuh",
    "pengen", "punya", "bisa", "ada", "yang", "dengan", "untuk", "buat",
    "di", "ke", "dari", "tapi", "dan", "atau", "kira", "kira-kira", "ya",
    "dong", "deh", "nih", "sih", "lah", "plis", "tolong", "mohon", "please",
    "oke", "ok", "halo", "hai",
}

# ======================================================
# FUNGSI UTAMA: preference_terms --- aggregated weights
# ======================================================
DEFAULT_WEIGHT = 5.0

ALL_CRITERIA = [
    "power",
    "handling",
    "efficiency",
    "driver_comfort",
    "passenger_comfort",
    "safety",
    "tech",
    "space",
    "offroad",
    "luxury",
    "lifecycle",
    "brand_strength",
    "price",
]

def resolve_preference_weights(
    preference_terms: List[str],
    entity_terms: List[str] = None,
    default: float = DEFAULT_WEIGHT,
) -> Dict[str, float]:
    """
    Mengubah list preference_terms dari NLU menjadi base_weight_profile
    untuk VIKOR slider.
    """
    weight_sum: Dict[str, float] = {c: 0.0 for c in ALL_CRITERIA}
    hit_count: Dict[str, int] = {c: 0 for c in ALL_CRITERIA}

    clean_terms = [
        t.strip().lower()
        for t in preference_terms
        if t.strip().lower() not in PREFERENCE_STOPWORDS and len(t.strip()) > 1
    ]

    print(f"[PREF MAP] Input terms: {preference_terms}")
    print(f"[PREF MAP] Clean terms (setelah filter stopwords): {clean_terms}")

    matched_terms = []
    for term in clean_terms:
        if term in PREFERENCE_WEIGHT_MAP:
            weights = PREFERENCE_WEIGHT_MAP[term]
            for criteria, val in weights.items():
                weight_sum[criteria] += val
                hit_count[criteria] += 1
            matched_terms.append(term)
            print(f"[PREF MAP] [EXACT] Exact match: '{term}' -> {weights}")
            continue

        mapper = get_mapper("preference_map", list(PREFERENCE_WEIGHT_MAP.keys()))
        matches = mapper.find_best_match(term, threshold=0.4)
        if matches:
            best_key, score = matches[0]
            weights = PREFERENCE_WEIGHT_MAP[best_key]
            for criteria, val in weights.items():
                weight_sum[criteria] += val * score
                hit_count[criteria] += 1
            matched_terms.append(f"{term}---{best_key}({score:.2f})")
            print(f"[PREF MAP] [SEMANTIC] Semantic match: '{term}' -> '{best_key}' (score: {score:.2f}) -> {weights}")
            continue

        print(f"[PREF MAP] [NONE] No match: '{term}' (tidak ada di peta)")

    print(f"[PREF MAP] Matched terms: {matched_terms}")

    final_weights: Dict[str, float] = {}
    for criteria in ALL_CRITERIA:
        if hit_count[criteria] > 0:
            avg = weight_sum[criteria] / hit_count[criteria]
            final_weights[criteria] = round(min(10.0, max(0.0, avg)), 1)
        else:
            final_weights[criteria] = float(GLOBAL_DEFAULT_PROFILE.get(criteria, default))

    print(f"[PREF MAP] Final weights (Decoupled): {final_weights}")
    return final_weights

# ======================================================
# CLUSTER DETECTION - COSINE SIMILARITY (BARU)
# ======================================================
def detect_cluster_from_weights(weights: Dict[str, float]) -> List[str]:
    """
    Mendeteksi cluster berdasarkan kemiripan kosinus antara vektor bobot user
    dan vektor centroid setiap cluster di CLUSTER_PROFILES.
    """
    user_vector = np.array([weights.get(c, 5.0) for c in ALL_CRITERIA])

    best_cluster = None
    best_similarity = -1.0
    SIMILARITY_THRESHOLD = 0.5

    for cluster_name, profile in CLUSTER_PROFILES.items():
        centroid = np.array([profile.get(c, 5.0) for c in ALL_CRITERIA])

        dot = np.dot(user_vector, centroid)
        norm_user = norm(user_vector)
        norm_centroid = norm(centroid)

        if norm_user == 0 or norm_centroid == 0:
            similarity = 0.0
        else:
            similarity = dot / (norm_user * norm_centroid)

        print(f"[CLUSTER] Cosine similarity dengan '{cluster_name}': {similarity:.3f}")

        if similarity > best_similarity:
            best_similarity = similarity
            best_cluster = cluster_name

    if best_similarity < SIMILARITY_THRESHOLD:
        print(f"[CLUSTER] Similarity tertinggi ({best_similarity:.3f}) < threshold ({SIMILARITY_THRESHOLD}). Kembali ke 'Global'.")
        return ["Global"]
    else:
        print(f"[CLUSTER] Cluster terpilih: '{best_cluster}' (similarity={best_similarity:.3f})")
        return [best_cluster]

# ======================================================
# ENTRY POINT: build_ui_state
# ======================================================
def build_ui_state(
    preference_terms: List[str],
    entity_terms: List[str] = None,
) -> Dict:
    """
    Entry point utama. Dipanggil dari endpoint /initial-ui-state.
    """
    entity_terms = entity_terms or []

    weights = resolve_preference_weights(preference_terms, entity_terms)
    clusters = detect_cluster_from_weights(weights)
    primary_cluster = clusters[0]

    cluster_profile = dict(CLUSTER_PROFILES.get(primary_cluster, GLOBAL_DEFAULT_PROFILE))

    final_profile = {}
    for c in ALL_CRITERIA:
        nlp_val = weights.get(c, 5.0)
        cluster_val = cluster_profile.get(c, 5.0)
        final_profile[c] = max(nlp_val, cluster_val)

    from ..feature_ontology import UI_TO_INDEX_MAP, CLUSTER_UI_NAMES

    ui_profile = {}
    for short_key, val in final_profile.items():
        ui_key = UI_TO_INDEX_MAP.get(short_key, short_key)
        ui_profile[ui_key] = val

    display_name = CLUSTER_UI_NAMES.get(primary_cluster, primary_cluster)

    return {
        "cluster_name": primary_cluster,
        "cluster_display_name": display_name,
        "all_clusters": clusters,
        "base_weight_profile": ui_profile,
    }