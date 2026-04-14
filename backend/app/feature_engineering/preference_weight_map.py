# backend/app/feature_engineering/preference_weight_map.py
#
# PETA PREFERENSI --- BOBOT VIKOR
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
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
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

from typing import Dict, List
from .semantic_mapper import get_mapper
from ..feature_ontology import GLOBAL_DEFAULT_PROFILE, CLUSTER_PROFILES

# ======================================================
# KAMUS UTAMA: PREFERENSI --- BOBOT MULTI-KRITERIA
# ======================================================

PREFERENCE_WEIGHT_MAP: Dict[str, Dict[str, float]] = {

    # --------- EFISIENSI / IRIT ---------------------------------------------------------------------------------------------------------------------------------------------------------
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

    # --------- PERFORMA / KENCANG ---------------------------------------------------------------------------------------------------------------------------------------------------
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

    # --------- HANDLING / KELINCAHAN ------------------------------------------------------------------------------------------------------------------------------------------
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

    # --------- KENYAMANAN ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
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

    # --------- PENGGUNAAN HARIAN ------------------------------------------------------------------------------------------------------------------------------------------------------
    # PERBAIKAN UTAMA: "harian" dan varian-nya sekarang memetakan ke
    # multi-kriteria yang relevan untuk penggunaan sehari-hari
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

    # --------- PERJALANAN JAUH / MUDIK ------------------------------------------------------------------------------------------------------------------------------------
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

    # --------- KELUARGA ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
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

    # --------- RUANG KABIN ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
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

    # --------- KEAMANAN ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
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

    # --------- TEKNOLOGI / FITUR ------------------------------------------------------------------------------------------------------------------------------------------------------
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

    # --------- MEWAH / PREMIUM ------------------------------------------------------------------------------------------------------------------------------------------------------------
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

    # --------- OFFROAD / TANGGUH ------------------------------------------------------------------------------------------------------------------------------------------------------
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

    # --------- AFTER SALES / PERAWATAN ------------------------------------------------------------------------------------------------------------------------------------
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

    # --------- REPUTASI / POPULARITAS ---------------------------------------------------------------------------------------------------------------------------------------
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

    # --------- NILAI JUAL KEMBALI ---------------------------------------------------------------------------------------------------------------------------------------------------
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

    # --------- SEGMEN ANAK MUDA / KULIAH ------------------------------------------------------------------------------------------------------------------------------
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

    # --------- MOBIL KEDUA / PEMULA ---------------------------------------------------------------------------------------------------------------------------------------------
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

    # --------- VALUE FOR MONEY ------------------------------------------------------------------------------------------------------------------------------------------------------------
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
# Kata-kata ini sering muncul dalam kalimat natural tapi
# bukan preferensi. Harus difilter SEBELUM mapping.
# ======================================================

PREFERENCE_STOPWORDS = {
    "sedang",       # "saya sedang cari" --- sedang = bukan preferensi
    "saya",
    "mau",
    "ingin",
    "cari",
    "cariin",
    "carikan",
    "butuh",
    "pengen",
    "punya",
    "bisa",
    "ada",
    "yang",
    "dengan",
    "untuk",
    "buat",
    "di",
    "ke",
    "dari",
    "tapi",
    "dan",
    "atau",
    "kira",
    "kira-kira",
    "ya",
    "dong",
    "deh",
    "nih",
    "sih",
    "lah",
    "plis",
    "tolong",
    "mohon",
    "please",
    "oke",
    "ok",
    "halo",
    "hai",
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

    Proses:
    1. Filter stopwords dari preference_terms
    2. Lookup tiap term ke PREFERENCE_WEIGHT_MAP
    3. Jika term tidak ditemukan persis, coba partial match
    4. Agregasi: rata-rata tertimbang dari semua term yang match
    5. Kriteria yang tidak ter-affect tetap di nilai default (5)

    Args:
        preference_terms : list preferensi dari NLU (sudah lowercase)
        entity_terms     : tambahan dari entity lain (body_type, powertrain, dll)
                           untuk konteks tambahan (opsional)
        default          : nilai default untuk kriteria yang tidak ter-affect

    Returns:
        Dict {kriteria: nilai 0-10}
    """

    # Inisialisasi akumulator murni (0.0)
    # Kita tidak ingin GLOBAL_DEFAULT_PROFILE (5.0) ikut meratakan/menurunkan (dilute) 
    # preferensi user jika user menyebutkan kata yang sangat spesifik (seperti 'sporty' = 8.0).
    weight_sum: Dict[str, float] = {c: 0.0 for c in ALL_CRITERIA}
    hit_count: Dict[str, int] = {c: 0 for c in ALL_CRITERIA}

    # Filter stopwords
    clean_terms = [
        t.strip().lower()
        for t in preference_terms
        if t.strip().lower() not in PREFERENCE_STOPWORDS and len(t.strip()) > 1
    ]

    print(f"[PREF MAP] Input terms: {preference_terms}")
    print(f"[PREF MAP] Clean terms (setelah filter stopwords): {clean_terms}")

    matched_terms = []

    for term in clean_terms:

        # 1. Exact match
        if term in PREFERENCE_WEIGHT_MAP:
            weights = PREFERENCE_WEIGHT_MAP[term]
            for criteria, val in weights.items():
                weight_sum[criteria] += val
                hit_count[criteria] += 1
            matched_terms.append(term)
            print(f"[PREF MAP] [EXACT] Exact match: '{term}' -> {weights}")
            continue

        # 2. Semantic match (scientific fallback)
        # Menggunakan TF-IDF + Cosine Similarity untuk mencari kemiripan makna
        mapper = get_mapper("preference_map", list(PREFERENCE_WEIGHT_MAP.keys()))
        matches = mapper.find_best_match(term, threshold=0.4) # Threshold disesuaikan

        if matches:
            best_key, score = matches[0] # Ambil yang paling mirip
            weights = PREFERENCE_WEIGHT_MAP[best_key]
            for criteria, val in weights.items():
                # Bobot dikalikan score similarity (makin mirip makin kuat)
                weight_sum[criteria] += val * score
                hit_count[criteria] += 1
            matched_terms.append(f"{term}---{best_key}({score:.2f})")
            print(f"[PREF MAP] [SEMANTIC] Semantic match: '{term}' -> '{best_key}' (score: {score:.2f}) -> {weights}")
            continue

        print(f"[PREF MAP] [NONE] No match: '{term}' (tidak ada di peta)")

    print(f"[PREF MAP] Matched terms: {matched_terms}")

    # Hitung rata-rata per kriteria
    final_weights: Dict[str, float] = {}
    for criteria in ALL_CRITERIA:
        if hit_count[criteria] > 0:
            avg = weight_sum[criteria] / hit_count[criteria]
            # Pastikan dalam range 0-10
            final_weights[criteria] = round(min(10.0, max(0.0, avg)), 1)
        else:
            # Tidak ada preferensi yang menyentuh kriteria ini 
            # -> Gunakan nilai dari GLOBAL_DEFAULT_PROFILE sebagai Fallback.
            # Ini krusial agar 'price' (Value for Money) tetap 10.0 meskipun user tidak mention 'irit'.
            final_weights[criteria] = float(GLOBAL_DEFAULT_PROFILE.get(criteria, default))

    print(f"[PREF MAP] Final weights (Decoupled): {final_weights}")
    return final_weights


# ======================================================
# CLUSTER DETECTION dari kombinasi preferensi
# ======================================================

CLUSTER_RULES = [
    # Format: (nama_cluster, {kriteria_yang_harus_dominan: threshold_minimum})
    # Diurut dari yang paling spesifik ke paling umum
    ("Family Comfort",      {"space": 8.0, "passenger_comfort": 7.0}),
    ("Rugged Explorer",     {"offroad": 8.0}),
    ("High-End Performance",{"power": 8.0, "handling": 7.0, "luxury": 6.0}),
    ("Urban Agility",       {"efficiency": 8.0, "handling": 7.0}),
    ("Practical All-Rounder",{"efficiency": 6.0, "space": 6.0, "driver_comfort": 6.0}),
    
    # Aturan tambahan
    ("Urban Agility",       {"price": 7, "tech": 7}), 
    ("High-End Performance",{"luxury": 8.0}),
]


def detect_cluster_from_weights(weights: Dict[str, float]) -> List[str]:
    """
    Mendeteksi cluster otomatis berdasarkan profil bobot yang sudah dihitung.
    Mendukung multi-cluster: mengembalikan semua yang cocok dengan threshold.

    Returns:
        List[str] Nama-nama cluster yang cocok
    """
    detected = []
    for cluster_name, conditions in CLUSTER_RULES:
        if all(weights.get(crit, 0) >= threshold for crit, threshold in conditions.items()):
            print(f"[CLUSTER] Logic Match: '{cluster_name}' dari conditions {conditions}")
            if cluster_name not in detected:
                detected.append(cluster_name)

    if not detected:
        return ["Global"]
    
    return detected


# ======================================================
# ENTRY POINT: dipanggil dari endpoint /initial-ui-state
# ======================================================

def build_ui_state(
    preference_terms: List[str],
    entity_terms: List[str] = None,
) -> Dict:
    """
    Entry point utama. Dipanggil dari endpoint /initial-ui-state.

    Returns dict yang langsung bisa direturn sebagai JSON response:
    {
        "cluster_name": str,
        "base_weight_profile": {kriteria: nilai, ...}
    }
    """
    entity_terms = entity_terms or []

    weights = resolve_preference_weights(preference_terms, entity_terms)
    clusters = detect_cluster_from_weights(weights)
    primary_cluster = clusters[0]

    # MERGE: Ambil base profile dari cluster yang terdeteksi
    cluster_profile = dict(CLUSTER_PROFILES.get(primary_cluster, GLOBAL_DEFAULT_PROFILE))
    
    # NLP weights (dari resolve_preference_weights) di-merge ke dalam cluster_profile.
    final_profile = {}
    for c in ALL_CRITERIA:
        nlp_val = weights.get(c, 5.0)
        cluster_val = cluster_profile.get(c, 5.0)
        final_profile[c] = max(nlp_val, cluster_val)

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # BRIDGE: Map Internal Keys -> UI Keys (INDEX_...)
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
    from ..feature_ontology import UI_TO_INDEX_MAP, CLUSTER_UI_NAMES
    
    ui_profile = {}
    for short_key, val in final_profile.items():
        ui_key = UI_TO_INDEX_MAP.get(short_key, short_key)
        ui_profile[ui_key] = val

    # Ambil Nama Indonesia untuk UI
    display_name = CLUSTER_UI_NAMES.get(primary_cluster, primary_cluster)

    return {
        "cluster_name": primary_cluster,
        "cluster_display_name": display_name,
        "all_clusters": clusters,
        "base_weight_profile": ui_profile, 
    }

