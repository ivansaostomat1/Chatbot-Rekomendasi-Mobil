import re
import requests

from rasa_sdk import Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.interfaces import Tracker
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet


API_URL = "http://localhost:8000/chat"


# ======================================================
# PREFERENCE NUMERIC & CLUSTER MAPPING
# ======================================================

NUMERIC_PREFERENCE_MAP = {
    "1": "irit",
    "2": "kencang",
    "3": "teknologi",
    "4": "nyaman"
}

NEED_CLUSTER_MAP = {
    "keluarga": "Family Car", "keluarga besar": "Family Car", "keluarga kecil": "Family Car", "mudik": "Family Car",
    "offroad": "Offroad", "banjir": "Offroad", "bebas banjir": "Offroad",
    "mewah": "Luxury",
}

PREFERENCE_CLUSTER_MAP = {
    "irit": "City Car", "hemat": "City Car", "bbm": "City Car",
    "keluarga": "Family Car", "luas": "Family Car",
    "kencang": "Performance", "ngebut": "Performance", "responsif": "Performance", "sporty": "Performance",
    "banjir": "Offroad", "jalan rusak": "Offroad",
    "luxury": "Luxury", "mewah": "Luxury"
}

PREFERENCE_INDEX_MAP = {
    "irit": "INDEX_EFFICIENCY", "hemat": "INDEX_EFFICIENCY", "bbm": "INDEX_EFFICIENCY",
    "kencang": "INDEX_PERFORMANCE", "ngebut": "INDEX_FUN_TO_DRIVE", "responsif": "INDEX_FUN_TO_DRIVE",
    "fun": "INDEX_FUN_TO_DRIVE", "sporty": "INDEX_FUN_TO_DRIVE", "enak dikendarai": "INDEX_FUN_TO_DRIVE", "gesit": "INDEX_FUN_TO_DRIVE",
    "nyaman": "INDEX_PASSENGER_COMFORT", "driver nyaman": "INDEX_DRIVER_COMFORT",
    "keluarga": "INDEX_SPACE", "luas": "INDEX_SPACE", "kabinnya luas": "INDEX_SPACE",
    "aman": "INDEX_SAFETY", "teknologi": "INDEX_TECH", "fitur": "INDEX_TECH", "fitur lengkap": "INDEX_TECH", "modern": "INDEX_TECH", "canggih": "INDEX_TECH",
    "mewah": "INDEX_LUXURY", "luxury": "INDEX_LUXURY", "banjir": "INDEX_OFFROAD", "jalan rusak": "INDEX_OFFROAD", "nanjak": "INDEX_PERFORMANCE"
}

CLUSTER_PROFILES = {
    "Family Car": {
        "INDEX_PERFORMANCE": 4, "INDEX_FUN_TO_DRIVE": 3, "INDEX_EFFICIENCY": 7,
        "INDEX_DRIVER_COMFORT": 6, "INDEX_PASSENGER_COMFORT": 8, "INDEX_SAFETY": 8,
        "INDEX_TECH": 6, "INDEX_SPACE": 9, "INDEX_OFFROAD": 2,
        "INDEX_LUXURY": 3, "INDEX_POPULARITY": 5, "INDEX_PRICE": 6,
    },
    "City Car": {
        "INDEX_PERFORMANCE": 4, "INDEX_FUN_TO_DRIVE": 4, "INDEX_EFFICIENCY": 9,
        "INDEX_DRIVER_COMFORT": 6, "INDEX_PASSENGER_COMFORT": 7, "INDEX_SAFETY": 6,
        "INDEX_TECH": 7, "INDEX_SPACE": 5, "INDEX_OFFROAD": 1,
        "INDEX_LUXURY": 2, "INDEX_POPULARITY": 6, "INDEX_PRICE": 8,
    },
    "Offroad": {
        "INDEX_PERFORMANCE": 8, "INDEX_FUN_TO_DRIVE": 6, "INDEX_EFFICIENCY": 3,
        "INDEX_DRIVER_COMFORT": 5, "INDEX_PASSENGER_COMFORT": 5, "INDEX_SAFETY": 7,
        "INDEX_TECH": 5, "INDEX_SPACE": 7, "INDEX_OFFROAD": 9,
        "INDEX_LUXURY": 3, "INDEX_POPULARITY": 4, "INDEX_PRICE": 4,
    },
    "Performance": {
        "INDEX_PERFORMANCE": 9, "INDEX_FUN_TO_DRIVE": 9, "INDEX_EFFICIENCY": 3,
        "INDEX_DRIVER_COMFORT": 7, "INDEX_PASSENGER_COMFORT": 4, "INDEX_SAFETY": 6,
        "INDEX_TECH": 7, "INDEX_SPACE": 3, "INDEX_OFFROAD": 2,
        "INDEX_LUXURY": 5, "INDEX_POPULARITY": 5, "INDEX_PRICE": 4,
    },
    "Luxury": {
        "INDEX_PERFORMANCE": 7, "INDEX_FUN_TO_DRIVE": 6, "INDEX_EFFICIENCY": 3,
        "INDEX_DRIVER_COMFORT": 9, "INDEX_PASSENGER_COMFORT": 9, "INDEX_SAFETY": 8,
        "INDEX_TECH": 9, "INDEX_SPACE": 7, "INDEX_OFFROAD": 2,
        "INDEX_LUXURY": 10, "INDEX_POPULARITY": 5, "INDEX_PRICE": 2,
    },
}


# ======================================================
# NEED CLASSIFICATION
# Clustered needs: punya cluster & hard filter langsung
# Lifestyle needs: ambigu, butuh pertanyaan prioritas
# ======================================================

CLUSTERED_NEED_TERMS = {
    "keluarga",
    "keluarga besar",
    "keluarga kecil",
    "offroad",
    "banjir",
    "bebas banjir",
    "mudik",
}

LIFESTYLE_NEED_TERMS = {
    "kuliah",
    "anak muda",
    "harian",
    "daily",
    "kantor",
    "kerja",
    "mobil kedua",
    "pemula",
    "perjalanan jauh",
}

# Semua need terms (union)
ALL_NEED_TERMS = CLUSTERED_NEED_TERMS | LIFESTYLE_NEED_TERMS


# ======================================================
# PREFERENSI YANG BERSIFAT SEKUNDER/TAMBAHAN
# ======================================================

SECONDARY_PREFERENCE_TERMS = {
    "canggih",
    "teknologi",
    "modern",
    "fitur",
    "fitur lengkap",
}


# ======================================================
# FIX 3: STOPWORDS — filter noise tokens
# ======================================================

STOPWORDS = {
    "cari", "mau", "ingin", "butuh", "yang", "dan", "atau",
    "untuk", "dengan", "ada", "punya", "dong", "nih", "yg",
    "saya", "aku", "gue", "gw",
}


# ======================================================
# FIX 1: NEW QUERY DETECTION
# ======================================================

def is_new_query(text: str) -> bool:
    """
    Detect if user message is a brand new search query.
    Returns True if user starts a new search (reset context needed).
    """
    text = text.lower().strip()
    new_query_triggers = [
        "mau mobil", "cari mobil", "ingin mobil", "butuh mobil",
        "mau cari", "tolong carikan", "rekomendasikan",
        "pengen mobil", "ganti mobil", "mobil baru",
    ]
    return any(t in text for t in new_query_triggers)


# ======================================================
# PARSE BUDGET
# ======================================================

def parse_budget(text):

    if not text:
        return None, None

    text = text.lower()

    text = text.replace("jutaan", "jt")
    text = text.replace("juta", "jt")
    text = text.replace("miliar", "m")
    text = text.replace("milyar", "m")

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
            # Budget > 1 Miliar: range -100jt s.d. +150jt
            min_budget = max(0, value - 100_000_000)
            max_budget = value + 150_000_000
        elif value <= 500_000_000:
            # Budget ≤ 500jt: range -50jt s.d. +100jt
            min_budget = max(0, value - 50_000_000)
            max_budget = value + 100_000_000
        else:
            # Budget 500jt - 1M: range -75jt s.d. +125jt
            min_budget = max(0, value - 75_000_000)
            max_budget = value + 125_000_000

        return min_budget, max_budget

    min_budget = int(numbers[0] * multiplier)
    max_budget = int(numbers[1] * multiplier)

    return min_budget, max_budget


# ======================================================
# EXTRACT ENTITIES (FIX 2: Clean entity split)
# ======================================================

def extract_entities(entities):

    preference_terms = []
    need_terms = []

    feature_entities = []
    body_entities = []
    powertrain_entities = []
    brand_entities = []
    hard_filter_entities = []

    min_budget = None
    max_budget = None

    for e in entities:

        value = str(e.get("value", "")).lower().strip()
        entity_type = e.get("entity")

        if entity_type == "preference":

            # Terjemahkan nomor pilihan ke preference string
            if value in NUMERIC_PREFERENCE_MAP:
                value = NUMERIC_PREFERENCE_MAP[value]

            # ======================================
            # FIX 2: SPLIT COMMA/SEMICOLON-JOINED VALUES
            # ONLY use sub-values, never re-insert original
            # ======================================
            sub_values = re.split(r'[,;/]+', value)
            sub_values = [v.strip() for v in sub_values if v.strip()]

            for sv in sub_values:
                # Terjemahkan ulang jika sub-value adalah nomor
                if sv in NUMERIC_PREFERENCE_MAP:
                    sv = NUMERIC_PREFERENCE_MAP[sv]

                # FIX 3: Filter stopwords
                if sv in STOPWORDS:
                    continue

                # NEED vs PREFERENCE SEPARATION
                if sv in ALL_NEED_TERMS:
                    need_terms.append(sv)
                elif len(sv) > 1:  # abaikan token sampah < 2 char ("a", "")
                    preference_terms.append(sv)

        elif entity_type == "feature":
            feature_entities.append(value)

        elif entity_type == "body_type":
            body_entities.append(value)

        elif entity_type == "powertrain":
            powertrain_entities.append(value)

        elif entity_type == "brand":
            brand_entities.append(value)

        elif entity_type == "hard_filter":
            # hard_filter entities langsung ke need_terms jika ada di ALL_NEED_TERMS
            if value in ALL_NEED_TERMS:
                need_terms.append(value)
            else:
                hard_filter_entities.append(value)

        elif entity_type == "budget":

            min_budget, max_budget = parse_budget(value)

    return {
        "need_terms": list(set(need_terms)),
        "preference_terms": preference_terms,
        "feature_entities": feature_entities,
        "body_entities": body_entities,
        "powertrain_entities": powertrain_entities,
        "brand_entities": brand_entities,
        "hard_filter_entities": hard_filter_entities,
        "min_budget": min_budget,
        "max_budget": max_budget
    }


# ======================================================
# DETERMINE TRIGGER: APAKAH PERLU TANYA PRIORITAS?
# ======================================================

def should_ask_priority(parsed: dict) -> tuple[bool, str]:
    """
    Returns (should_ask: bool, reason: str)
    """

    need_terms = parsed["need_terms"]
    preference_terms = parsed["preference_terms"]

    has_clustered_need = any(n in CLUSTERED_NEED_TERMS for n in need_terms)
    has_lifestyle_need = any(n in LIFESTYLE_NEED_TERMS for n in need_terms)

    # Filter preferensi yang bukan sekunder
    primary_preferences = [p for p in preference_terms if p not in SECONDARY_PREFERENCE_TERMS]

    # Cek apakah ada entity lain yang sudah menjadi constraint kuat
    has_other_constraints = bool(
        parsed.get("body_entities") or 
        parsed.get("powertrain_entities") or 
        parsed.get("brand_entities") or 
        parsed.get("feature_entities") or 
        parsed.get("hard_filter_entities")
    )

    # [CASE 1] Tidak ada need dan tidak ada preference → tanya
    if not need_terms and not preference_terms:
        if has_other_constraints:
            return False, "Tidak ada butuh/preference namun ada filter spesifik lain"
        return True, "Tidak ada need maupun preference"

    # [CASE 2] Hanya lifestyle need tanpa primary preference → tanya
    if has_lifestyle_need and not has_clustered_need and not primary_preferences:
        return True, f"Hanya lifestyle need ({need_terms}) tanpa preferensi jelas"

    # [CASE 3] Ada 2+ primary preference yang masuk (user butuh ranking prioritas)
    if len(primary_preferences) >= 2:
        return True, f"Ada {len(primary_preferences)} preferensi: {primary_preferences}"

    return False, "Sudah ada cukup informasi"




# ======================================================
# BUILD BACKEND PAYLOAD
# ======================================================

def extract_cluster_name(need_terms, preference_terms):
    clusters = []
    for need in need_terms:
        if need in NEED_CLUSTER_MAP:
            clusters.append(NEED_CLUSTER_MAP[need])
    for pref in preference_terms:
        if pref in PREFERENCE_CLUSTER_MAP:
            clusters.append(PREFERENCE_CLUSTER_MAP[pref])
    if not clusters:
        return "Global"
    return max(set(clusters), key=clusters.count)

def build_backend_payload(parsed: dict, user_message: str = None) -> dict:
    need_terms = parsed["need_terms"]
    preference_terms = parsed["preference_terms"]
    has_clustered_need = any(n in CLUSTERED_NEED_TERMS for n in need_terms)

    cluster_name = extract_cluster_name(need_terms, preference_terms)
    
    # ──────────────────────────────────────────────────────
    # base_weight_profile → HANYA untuk UI slider defaults
    # (bukan untuk VIKOR — VIKOR pakai manual_weights dari user)
    # ──────────────────────────────────────────────────────
    GLOBAL_DEFAULT = {
        "INDEX_PERFORMANCE": 5, "INDEX_FUN_TO_DRIVE": 5, "INDEX_EFFICIENCY": 5,
        "INDEX_DRIVER_COMFORT": 5, "INDEX_PASSENGER_COMFORT": 5, "INDEX_SAFETY": 5,
        "INDEX_TECH": 5, "INDEX_SPACE": 5, "INDEX_OFFROAD": 5,
        "INDEX_LUXURY": 5, "INDEX_POPULARITY": 5, "INDEX_PRICE": 5,
    }
    base_weight_profile = dict(CLUSTER_PROFILES.get(cluster_name, GLOBAL_DEFAULT))

    # Boost slider defaults berdasarkan NLP preference (suggestion only)
    weight_input = {}
    for p in preference_terms:
        boost_score = 6 if has_clustered_need and p in SECONDARY_PREFERENCE_TERMS else 9
        weight_input[p] = boost_score
        
        if p in PREFERENCE_INDEX_MAP:
            idx_name = PREFERENCE_INDEX_MAP[p]
            base_weight_profile[idx_name] = max(base_weight_profile.get(idx_name, 0), boost_score)

    entities_combined = (
        parsed["feature_entities"]
        + parsed["body_entities"]
        + parsed["powertrain_entities"]
        + parsed["brand_entities"]
        + parsed["hard_filter_entities"]
    )

    payload = {
        "user_message": user_message,
        "preference_terms": preference_terms,
        "need_terms": need_terms,
        "weight_input": weight_input,
        "base_weight_profile": base_weight_profile,
        "cluster_name": cluster_name,
        "entities": entities_combined,
        "min_budget": parsed["min_budget"],
        "max_budget": parsed["max_budget"]
    }

    return payload


# ======================================================
# FORMAT HASIL REKOMENDASI
# ======================================================

def format_car_recommendation(cars):

    message = f"Berikut {len(cars)} rekomendasi mobil terbaik untuk kamu:\n\n"

    for car in cars:

        brand = car.get("BRAND")
        model = car.get("MODEL")
        varian = car.get("VARIAN")

        price = car.get("HARGAOTR") or 0
        price_str = f"{price:,}".replace(",", ".")

        message += f"- {brand} {model} {varian} (Rp{price_str})\n"

    return message


# ======================================================
# RASA ACTION
# ======================================================

class ActionRecommendCar(Action):

    def name(self):
        return "action_recommend_car"

    def run(self, dispatcher, tracker, domain):

        text = tracker.latest_message.get("text", "")
        entities = tracker.latest_message.get("entities", [])

        print("==================================================")
        print(f"[RASA ACTION] Menerima pesan: '{text}'")
        print(f"[RASA ACTION] Entities dari NLU: {entities}")

        parsed = extract_entities(entities)

        # =================================================
        # FIX 1: DETECT NEW QUERY → RESET ALL CONTEXT
        # =================================================

        new_query = is_new_query(text)

        if new_query:
            print("[RASA ACTION] 🔄 NEW QUERY DETECTED → Mereset seluruh konteks sesi.")
            prev_preferences = []
            prev_needs = []
            prev_features = []
            prev_brands = []
            prev_powertrains = []
            prev_bodies = []
            prev_hard_filters = []
            prev_min_budget = None
            prev_max_budget = None
            # FIX 4: Reset priority_asked
            priority_already_asked = False
        else:
            print("[RASA ACTION] 🔄 Menggabungkan Kriteria dengan memori konteks (Update Default).")
            prev_preferences = tracker.get_slot("preference") or []
            prev_needs = tracker.get_slot("need") or []
            
            def _to_list(val):
                if val is None: return []
                if isinstance(val, list): return val
                return [val]

            prev_features = _to_list(tracker.get_slot("feature"))
            prev_brands = _to_list(tracker.get_slot("brand"))
            prev_powertrains = _to_list(tracker.get_slot("powertrain"))
            prev_bodies = _to_list(tracker.get_slot("body_type"))
            prev_hard_filters = _to_list(tracker.get_slot("hard_filter"))

            prev_min_budget = tracker.get_slot("min_budget")
            prev_max_budget = tracker.get_slot("max_budget")
            priority_already_asked = tracker.get_slot("priority_asked") or False

        def unique_clean(lst):
            return list(set([str(x).strip().lower() for x in lst if x]))

        # Merge (akan kosong jika new_query karena prev_* sudah di-reset)
        parsed["preference_terms"] = unique_clean(parsed["preference_terms"] + prev_preferences)
        
        # FIX 3: Filter stopwords dari preference_terms
        parsed["preference_terms"] = [
            p for p in parsed["preference_terms"]
            if p not in STOPWORDS and p not in ALL_NEED_TERMS and len(p) > 2
        ]

        parsed["need_terms"] = unique_clean(parsed["need_terms"] + prev_needs)

        # Budget hanya mengikuti prev_budget jika user TIDAK menspesifikasikan budget baru
        if parsed["min_budget"] is None:
            parsed["min_budget"] = prev_min_budget

        if parsed["max_budget"] is None:
            parsed["max_budget"] = prev_max_budget

        # Pisahkan memory per tipe entitas
        parsed["feature_entities"] = unique_clean(parsed["feature_entities"] + prev_features)
        parsed["brand_entities"] = unique_clean(parsed["brand_entities"] + prev_brands)
        parsed["powertrain_entities"] = unique_clean(parsed["powertrain_entities"] + prev_powertrains)
        parsed["body_entities"] = unique_clean(parsed["body_entities"] + prev_bodies)
        parsed["hard_filter_entities"] = unique_clean(parsed["hard_filter_entities"] + prev_hard_filters)

        print(f"[RASA ACTION] Parsed need_terms: {parsed['need_terms']}")
        print(f"[RASA ACTION] Parsed preference_terms: {parsed['preference_terms']}")

        # =================================================
        # LOGIKA PERTANYAAN PRIORITAS
        # =================================================

        ask_priority, reason = should_ask_priority(parsed)

        if ask_priority and not priority_already_asked:

            dispatcher.utter_message(text="""Apa yang paling kamu prioritaskan?

1️⃣ irit bahan bakar  
2️⃣ performa kencang  
3️⃣ teknologi canggih  
4️⃣ kenyamanan""")

            print(f"[RASA ACTION] Bertanya prioritas ke user. Alasan: {reason}")
            print("==================================================")

            return [
                SlotSet("min_budget", parsed["min_budget"]),
                SlotSet("max_budget", parsed["max_budget"]),
                SlotSet("need", parsed["need_terms"]),
                SlotSet("preference", parsed["preference_terms"]),
                SlotSet("priority_asked", True),
            ]

        # Jika priority sudah ditanya, langsung lanjut ke backend
        if priority_already_asked:
            print(f"[RASA ACTION] Priority sudah ditanya sebelumnya, skip ke backend.")

        # =================================================
        # KIRIM KE FASTAPI ATAU MINTA BOBOT KE FRONTEND
        # =================================================

        payload = build_backend_payload(parsed, text)

        print(f"[RASA ACTION] Menghentikan flow untuk meminta input bobot manual dari frontend.")
        print(f"[RASA ACTION] Payload siap kirim ke FastAPI: {payload}")

        dispatcher.utter_message(
            text="Silakan atur bobot kriteria yang paling penting menurut Anda (misal: Performa, Irit, Kenyamanan).",
            custom={
                "action": "ask_weights",
                "payload": payload
            }
        )

        print("[RASA ACTION] Selesai memproses pesan, menunggu frontend.")
        print("==================================================")

        return [
            SlotSet("min_budget", parsed["min_budget"]),
            SlotSet("max_budget", parsed["max_budget"]),
            SlotSet("preference", parsed["preference_terms"]),
            SlotSet("need", parsed["need_terms"]),
            SlotSet("feature", parsed["feature_entities"]),
            SlotSet("brand", parsed["brand_entities"]),
            SlotSet("powertrain", parsed["powertrain_entities"]),
            SlotSet("body_type", parsed["body_entities"]),
            SlotSet("hard_filter", parsed["hard_filter_entities"]),
            # FIX 4: Reset priority di akhir setiap query baru agar sesi berikutnya mulai fresh
            SlotSet("priority_asked", False if new_query else priority_already_asked),
        ]