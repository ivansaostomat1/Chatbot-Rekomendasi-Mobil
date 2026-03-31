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
    "kencang": "Performance", "ngebut": "Performance", "responsif": "Performance", "sporty": "Performance", "nggak lelet": "Performance",
    "banjir": "Offroad", "jalan rusak": "Offroad",
    "luxury": "Luxury", "mewah": "Luxury"
}

PREFERENCE_INDEX_MAP = {
    "irit": ["INDEX_EFFICIENCY"], "hemat": ["INDEX_EFFICIENCY"], "bbm": ["INDEX_EFFICIENCY"],
    "kencang": ["INDEX_POWER", "INDEX_HANDLING"], "nggak lelet": ["INDEX_POWER", "INDEX_HANDLING"], "ngebut": ["INDEX_POWER"], "responsif": ["INDEX_POWER"],
    "fun": ["INDEX_HANDLING"], "sporty": ["INDEX_POWER", "INDEX_HANDLING", "INDEX_DRIVER_COMFORT"], "enak dikendarai": ["INDEX_HANDLING", "INDEX_DRIVER_COMFORT"], "gesit": ["INDEX_HANDLING"], "lincah": ["INDEX_HANDLING"], "enak dibawa": ["INDEX_HANDLING"], "handlingnya enak": ["INDEX_HANDLING"],
    "nyaman": ["INDEX_PASSENGER_COMFORT"], "driver nyaman": ["INDEX_DRIVER_COMFORT"],
    "keluarga": ["INDEX_SPACE"], "luas": ["INDEX_SPACE"], "kabinnya luas": ["INDEX_SPACE"],
    "aman": ["INDEX_SAFETY"], "teknologi": ["INDEX_TECH"], "fitur": ["INDEX_TECH"], "fitur lengkap": ["INDEX_TECH"], "modern": ["INDEX_TECH"], "canggih": ["INDEX_TECH"],
    "mewah": ["INDEX_LUXURY"], "luxury": ["INDEX_LUXURY"], "banjir": ["INDEX_OFFROAD"], "jalan rusak": ["INDEX_OFFROAD"], "nanjak": ["INDEX_POWER"]
}

CLUSTER_PROFILES = {
    "Family Car": {
        "INDEX_POWER": 4, "INDEX_HANDLING": 5, "INDEX_EFFICIENCY": 7,
        "INDEX_DRIVER_COMFORT": 6, "INDEX_PASSENGER_COMFORT": 8, "INDEX_SAFETY": 8,
        "INDEX_TECH": 6, "INDEX_SPACE": 9, "INDEX_OFFROAD": 2,
        "INDEX_LUXURY": 3, "INDEX_PRICE": 10,
    },
    "City Car": {
        "INDEX_POWER": 4, "INDEX_HANDLING": 7, "INDEX_EFFICIENCY": 9,
        "INDEX_DRIVER_COMFORT": 6, "INDEX_PASSENGER_COMFORT": 7, "INDEX_SAFETY": 6,
        "INDEX_TECH": 7, "INDEX_SPACE": 5, "INDEX_OFFROAD": 1,
        "INDEX_LUXURY": 2, "INDEX_PRICE": 10,
    },
    "Offroad": {
        "INDEX_POWER": 8, "INDEX_HANDLING": 4, "INDEX_EFFICIENCY": 3,
        "INDEX_DRIVER_COMFORT": 5, "INDEX_PASSENGER_COMFORT": 5, "INDEX_SAFETY": 7,
        "INDEX_TECH": 5, "INDEX_SPACE": 7, "INDEX_OFFROAD": 9,
        "INDEX_LUXURY": 3, "INDEX_PRICE": 10,
    },
    "Performance": {
        "INDEX_POWER": 9, "INDEX_HANDLING": 9, "INDEX_EFFICIENCY": 3,
        "INDEX_DRIVER_COMFORT": 7, "INDEX_PASSENGER_COMFORT": 4, "INDEX_SAFETY": 6,
        "INDEX_TECH": 7, "INDEX_SPACE": 3, "INDEX_OFFROAD": 2,
        "INDEX_LUXURY": 5, "INDEX_PRICE": 10,
    },
    "Luxury": {
        "INDEX_POWER": 7, "INDEX_HANDLING": 7, "INDEX_EFFICIENCY": 3,
        "INDEX_DRIVER_COMFORT": 9, "INDEX_PASSENGER_COMFORT": 9, "INDEX_SAFETY": 8,
        "INDEX_TECH": 9, "INDEX_SPACE": 7, "INDEX_OFFROAD": 2,
        "INDEX_LUXURY": 10, "INDEX_PRICE": 10,
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
    "saya", "aku", "gue", "gw", "kalo", "bisa", "saja", "apa",
    "siapa", "dimana", "kapan", "bagaimana", "kenapa", "yg",
}

# ======================================================
# RELEVANT KEYWORDS FOR SAFETY NET
# ======================================================

VALID_REFINE_KEYWORDS = (
    set(PREFERENCE_INDEX_MAP.keys()) | 
    ALL_NEED_TERMS | 
    {"bensin", "diesel", "hybrid", "listrik", "ev", "hibrida", "solar", "battery"} |
    {"suv", "mpv", "sedan", "hatchback", "coupe", "wagon", "sport", "city car"} |
    {"toyota", "honda", "suzuki", "mitsubishi", "nissan", "mazda", "hyundai", "kia", "wuling", "chery", "daihatsu", "byd", "mg", "gwm", "bmw", "mercedes"} |
    {"sunroof", "panoramic", "camera", "360", "charger", "wireless", "apple", "android"}
)


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
        "ada mobil", "mobil apa"
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

def extract_entities(entities, text=None):

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

    # ======================================================
    # FIX 6: MANUAL KEYWORD EXTRACTION (SAFETY NET)
    # If Rasa missed some obvious keywords in short refinements.
    # ======================================================
    if text:
        text_lower = text.lower()
        
        # Powertrain check
        for p in ["bensin", "diesel", "hybrid", "listrik", "ev", "hibrida"]:
            p_clean = "hybrid" if p == "hibrida" else p
            if p in text_lower and p_clean not in powertrain_entities:
                powertrain_entities.append(p_clean)
        
        # Body type check
        for b in ["suv", "mpv", "sedan", "hatchback", "coupe", "wagon"]:
            if b in text_lower and b not in body_entities:
                body_entities.append(b)
        
        # BRAND check (common ones)
        for br in ["toyota", "honda", "suzuki", "mitsubishi", "nissan", "mazda", "hyundai", "kia", "wuling", "chery", "daihatsu"]:
            if br in text_lower and br not in brand_entities:
                brand_entities.append(br)

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
        "INDEX_POWER": 5, "INDEX_HANDLING": 5, "INDEX_EFFICIENCY": 5,
        "INDEX_DRIVER_COMFORT": 5, "INDEX_PASSENGER_COMFORT": 5, "INDEX_SAFETY": 5,
        "INDEX_TECH": 5, "INDEX_SPACE": 5, "INDEX_OFFROAD": 5,
        "INDEX_LUXURY": 5, "INDEX_PRICE": 10,
    }
    base_weight_profile = dict(CLUSTER_PROFILES.get(cluster_name, GLOBAL_DEFAULT))

    # Boost slider defaults berdasarkan NLP preference (suggestion only)
    weight_input = {}
    for p in preference_terms:
        boost_score = 6 if has_clustered_need and p in SECONDARY_PREFERENCE_TERMS else 9
        weight_input[p] = boost_score
        
        if p in PREFERENCE_INDEX_MAP:
            indices = PREFERENCE_INDEX_MAP[p]
            if isinstance(indices, str):
                indices = [indices]
            for idx_name in indices:
                base_weight_profile[idx_name] = max(base_weight_profile.get(idx_name, 0), boost_score)
                
    # Sesuai permintaan user: VFM (Price) selalu maksimal (10)
    base_weight_profile["INDEX_PRICE"] = 10.0

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

        parsed = extract_entities(entities, text=text)

        # =================================================
        # FIX 1: DETECT NEW QUERY → RESET ALL CONTEXT
        # =================================================

        new_query = is_new_query(text)

        # =================================================
        # FIX 5: GUARD AGAINST EMPTY INPUTS (OUT OF DOMAIN CHAT)
        # We only reject if it's NOT a new query AND it has NO entities AND it has NO relevant keywords.
        # This prevents "kalo bisa yang bensin saja" from being rejected even if NLU misses "bensin".
        # =================================================
        has_car_keywords = any(k in text.lower() for k in VALID_REFINE_KEYWORDS)
        
        if not entities and not new_query and not has_car_keywords:
            print(f"[RASA ACTION] ❌ TERDETEKSI PESAN ASAL/OUT-OF-DOMAIN: '{text}'. Mengeksekusi fallback action.")
            dispatcher.utter_message(response="utter_default")
            return []

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
        ]


class ActionCompareBudget(Action):

    def name(self):
        return "action_compare_budget"

    def run(self, dispatcher, tracker, domain):
        text = tracker.latest_message.get("text", "")
        entities = tracker.latest_message.get("entities", [])
        
        # 1. Dapatkan budget lama dari slot
        prev_max_budget = tracker.get_slot("max_budget")
        
        # 2. Parse budget baru dari pesan user
        parsed = extract_entities(entities, text=text)
        new_max_budget = parsed["max_budget"]
        new_min_budget = parsed["min_budget"]

        # Jika user tidak menyebut budget baru secara spesifik, tapi tanya "kalau nambah"
        # Kita bisa asumsikan increment (misal default +50jt jika sulit di-parse)
        if not new_max_budget and prev_max_budget:
            # Cari angka di text (misal "nambah 50jt")
            numbers = re.findall(r"\d+", text.lower().replace("jt", "000000"))
            if numbers:
                increment = int(numbers[0])
                if increment < 1000: # Masih dalam satuan Juta (misal "nambah 50")
                    increment *= 1_000_000
                new_max_budget = prev_max_budget + increment
            else:
                # Default increment if nothing found
                new_max_budget = prev_max_budget + 50_000_000

        if not new_max_budget:
            dispatcher.utter_message(text="Berapa budget baru yang ingin kamu bandingkan?")
            return []

        # 3. Kumpulkan kriteria lain dari slot (Context Persistence)
        current_slots = {
            "preference_terms": tracker.get_slot("preference") or [],
            "need_terms": tracker.get_slot("need") or [],
            "entities": (
                (tracker.get_slot("feature") or []) +
                (tracker.get_slot("brand") or []) +
                (tracker.get_slot("powertrain") or []) +
                (tracker.get_slot("body_type") or []) +
                (tracker.get_slot("hard_filter") or [])
            ),
            "min_budget": new_min_budget or tracker.get_slot("min_budget"),
            "max_budget": new_max_budget,
            "previous_max_budget": prev_max_budget
        }

        payload = build_backend_payload({
            "need_terms": current_slots["need_terms"],
            "preference_terms": current_slots["preference_terms"],
            "feature_entities": tracker.get_slot("feature") or [],
            "body_entities": tracker.get_slot("body_type") or [],
            "powertrain_entities": tracker.get_slot("powertrain") or [],
            "brand_entities": tracker.get_slot("brand") or [],
            "hard_filter_entities": tracker.get_slot("hard_filter") or [],
            "min_budget": current_slots["min_budget"],
            "max_budget": current_slots["max_budget"]
        }, text)
        
        # Tambahkan previous_max_budget ke payload
        payload["previous_max_budget"] = prev_max_budget

        print(f"[RASA ACTION] 📊 Comparing budget: {prev_max_budget} -> {new_max_budget}")

        # Langsung panggil backend (Search Mode)
        try:
            response = requests.post(API_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            
            cars = data.get("recommendations", [])
            comparison_insight = data.get("comparison_insight")

            if not cars:
                dispatcher.utter_message(text="Maaf, saya tidak menemukan mobil yang cocok dengan budget baru tersebut.")
                return []

            # Format Response
            msg = f"Baik, dengan budget baru maksimal Rp{new_max_budget:,.0f}...\n\n"
            if comparison_insight:
                msg += f"💡 **Analisa:** {comparison_insight}\n\n"
            
            msg += format_car_recommendation(cars)
            
            # Tambahkan detail insight per mobil
            msg += "\nKenapa mobil ini?\n"
            for car in cars[:2]:
                msg += f"- {car['MODEL']}: {car.get('insight', 'Pilihan seimbang.')}\n"

            dispatcher.utter_message(text=msg)

        except Exception as e:
            print(f"[RASA ACTION] Error calling backend: {e}")
            dispatcher.utter_message(text="Maaf, terjadi kendala saat memproses perbandingan budget.")

        return [
            SlotSet("max_budget", new_max_budget),
            SlotSet("min_budget", new_min_budget) if new_min_budget else SlotSet("min_budget", tracker.get_slot("min_budget"))
        ]