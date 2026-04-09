import re
import requests

from rasa_sdk import Action
from rasa_sdk.interfaces import Tracker
from rasa_sdk.events import SlotSet
from actions.context_manager import DialogueContextManager

API_URL = "http://localhost:8000/chat"
API_UI_URL = "http://localhost:8000/initial-ui-state"

# ======================================================
# EXTRACT ENTITIES MURNI (TANPA HARDCODED ONTOLOGY)
# ======================================================

def extract_entities(entities, text=None):

    preference_terms = []
    feature_entities = []
    body_entities = []
    powertrain_entities = []
    brand_entities = []
    hard_filter_entities = []
    negated_entities = []
    raw_budgets = []

    for e in entities:
        value = str(e.get("value", "")).lower().strip()
        entity_type = e.get("entity")

    # HEURISTIK KESELAMATAN (Negation Safety Net)
    # Jika NLU gagal mendeteksi role='negated', kita cek kata-kata di sekitarnya
    negation_keywords = ["jangan", "tidak", "bukan", "anti", "selain", "asal jangan", "gamau", "ga mau"]
    
    for e in entities:
        value = str(e.get("value", "")).lower().strip()
        entity_type = e.get("entity")
        start = e.get("start", 0)
        
        # 1. CEK ML ROLE
        is_negated = (e.get("role") == "negated")
        
        # 2. CEK HEURISTIK (Backup jika ML gagal)
        if not is_negated and text:
            # Ambil potongan teks sebelum entitas (misal 15 karakter sebelumnya)
            context_before = text[max(0, start-15):start].lower()
            for kw in negation_keywords:
                if kw in context_before:
                    print(f"[RASA ACTION] [SAFETY NET] Terdeteksi kata negasi '{kw}' sebelum '{value}'. Menandai sebagai negated.")
                    is_negated = True
                    break

        if is_negated:
            print(f"[RASA ACTION] [NEGATED] Mengabaikan entitas '{value}' ({entity_type}) karena di-tag sebagai 'negated'.")
            negated_entities.append(value)
            continue

        if entity_type == "preference":
            sub_values = re.split(r'[,;/]+', value)
            sub_values = [v.strip() for v in sub_values if v.strip()]
            for sv in sub_values:
                if len(sv) > 1:
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
            hard_filter_entities.append(value)

        elif entity_type == "min_seat":
            try:
                seat_count = int(re.search(r'\d+', value).group())
                hard_filter_entities.append(f"{seat_count} seat")
            except:
                pass

        elif entity_type == "budget":
            raw_budgets.append(value)

    return {
        "preference_terms": preference_terms,
        "feature_entities": feature_entities,
        "body_entities": body_entities,
        "powertrain_entities": powertrain_entities,
        "brand_entities": brand_entities,
        "hard_filter_entities": hard_filter_entities,
        "negated_entities": negated_entities,
        "raw_budgets": raw_budgets
    }


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
        intent_name = tracker.latest_message.get("intent", {}).get("name")

        print("==================================================")
        print(f"[RASA ACTION] Menerima pesan: '{text}'")
        print(f"[RASA ACTION] Intent terdeteksi: {intent_name}")
        print(f"[RASA ACTION] Entities dari NLU: {entities}")

        # Pendelegasian Out Of Scope ke fallback policy / utter_default
        if intent_name == "out_of_scope":
            print(f"[RASA ACTION] ❌ TERDETEKSI PESAN OUT-OF-DOMAIN: '{text}'. Mengeksekusi fallback action.")
            dispatcher.utter_message(response="utter_default")
            return []

        parsed = extract_entities(entities, text=text)
        new_query = (intent_name == "start_search")

        if new_query:
            print("[RASA ACTION] 🔄 NEW QUERY DETECTED → Mereset seluruh konteks sesi.")
            prev_min_budget = None
            prev_max_budget = None
        else:
            print("[RASA ACTION] 🔄 Menggabungkan Kriteria dengan memori konteks melalui OOP.")
            prev_min_budget = tracker.get_slot("min_budget")
            prev_max_budget = tracker.get_slot("max_budget")

        # Mendelegasikan list merging dan deduplication ke class terpisah
        ctx_manager = DialogueContextManager(tracker, parsed, reset_context=new_query)
        merged_context = ctx_manager.get_merged_context()

        entities_combined = (
            merged_context["feature_entities"]
            + merged_context["body_entities"]
            + merged_context["powertrain_entities"]
            + merged_context["brand_entities"]
            + merged_context["hard_filter_entities"]
        )

        print(f"[RASA ACTION] Merged context: preferences={merged_context['preference_terms']}, entities={entities_combined}")

        payload = {
            "user_message": text,
            "preference_terms": merged_context["preference_terms"],
            "need_terms": [],
            "weight_input": {},
            "entities": entities_combined,
            "negated_terms": merged_context["negated_terms"],
            "raw_budgets": merged_context["raw_budgets"],
            "min_budget": prev_min_budget,
            "max_budget": prev_max_budget
        }

        print(f"[RASA ACTION] Meminta profil bobot dan klasterisasi dari backend...")
        try:
            ui_resp = requests.post(API_UI_URL, json={
                "preference_terms": merged_context["preference_terms"],
                "need_terms": [],
                "entities": entities_combined
            })
            ui_resp.raise_for_status()
            ui_data = ui_resp.json()
            
            payload["cluster_name"] = ui_data.get("cluster_name", "Global")
            payload["base_weight_profile"] = ui_data.get("base_weight_profile", {})
            
            print(f"[RASA ACTION] Terdeteksi cluster: {payload['cluster_name']}")
        except Exception as e:
            print(f"[RASA ACTION] [ERROR] Gagal mengambil profil awal: {e}")
            payload["cluster_name"] = "Global"
            payload["base_weight_profile"] = {}

        if new_query:
            print(f"[RASA ACTION] [NEW QUERY] Meminta input bobot manual dari frontend.")
            dispatcher.utter_message(
                text="Silakan atur bobot kriteria yang paling penting menurut Anda (misal: Performa, Irit, Kenyamanan).",
                custom={
                    "action": "ask_weights",
                    "payload": payload
                }
            )
        else:
            print(f"[RASA ACTION] [REFINEMENT] Langsung mencari mobil dengan payload: {payload}")
            dispatcher.utter_message(
                text="Baik, kriteria pencarian sedang saya sesuaikan...",
                custom={
                    "action": "search_cars",
                    "payload": payload
                }
            )

        print("[RASA ACTION] Selesai memproses pesan, menunggu respon.")
        print("==================================================")

        return [
            SlotSet("preference", merged_context["preference_terms"]),
            SlotSet("feature", merged_context["feature_entities"]),
            SlotSet("brand", merged_context["brand_entities"]),
            SlotSet("powertrain", merged_context["powertrain_entities"]),
            SlotSet("body_type", merged_context["body_entities"]),
            SlotSet("hard_filter", merged_context["hard_filter_entities"]),
            SlotSet("raw_budgets", merged_context["raw_budgets"]),
            SlotSet("negated_terms", merged_context["negated_terms"]),
        ]


class ActionCompareBudget(Action):

    def name(self):
        return "action_compare_budget"

    def run(self, dispatcher, tracker, domain):
        text = tracker.latest_message.get("text", "")
        entities = tracker.latest_message.get("entities", [])
        
        prev_max_budget = tracker.get_slot("max_budget")
        
        parsed = extract_entities(entities, text=text)
        
        payload = {
            "preference_terms": tracker.get_slot("preference") or [],
            "need_terms": tracker.get_slot("need") or [],
            "entities": (
                (tracker.get_slot("feature") or []) +
                (tracker.get_slot("brand") or []) +
                (tracker.get_slot("powertrain") or []) +
                (tracker.get_slot("body_type") or []) +
                (tracker.get_slot("hard_filter") or [])
            ),
            "min_budget": tracker.get_slot("min_budget"),
            "max_budget": tracker.get_slot("max_budget"), 
            "previous_max_budget": prev_max_budget,
            "raw_budgets": parsed["raw_budgets"]
        }
        
        if not parsed["raw_budgets"]:
            numbers = re.findall(r"\d+", text.lower().replace("jt", "000000"))
            if numbers:
                increment = int(numbers[0])
                if increment < 1000:
                    increment *= 1_000_000
                if prev_max_budget:
                    payload["max_budget"] = prev_max_budget + increment
            else:
                if prev_max_budget:
                    payload["max_budget"] = prev_max_budget + 50_000_000
                else:
                    dispatcher.utter_message(text="Berapa budget baru yang ingin kamu bandingkan?")
                    return []

        print(f"[RASA ACTION] 📊 Comparing budget payload: {payload}")

        try:
            response = requests.post(API_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            
            cars = data.get("recommendations", [])
            comparison_insight = data.get("comparison_insight")

            if not cars:
                dispatcher.utter_message(text="Maaf, saya tidak menemukan mobil yang cocok dengan budget baru tersebut.")
                return []

            msg = f"Baik, membandingkan opsi dengan budget yang diatur ulang:\n\n"
            if comparison_insight:
                msg += f"💡 **Analisa:** {comparison_insight}\n\n"
            
            msg += format_car_recommendation(cars)
            
            msg += "\nKenapa mobil ini?\n"
            for car in cars[:2]:
                msg += f"- {car['MODEL']}: {car.get('insight', 'Pilihan seimbang.')}\n"

            dispatcher.utter_message(text=msg)

        except Exception as e:
            print(f"[RASA ACTION] Error calling backend: {e}")
            dispatcher.utter_message(text="Maaf, terjadi kendala saat memproses perbandingan budget.")

        return []