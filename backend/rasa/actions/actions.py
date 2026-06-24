import re
import requests

from rasa_sdk import Action
from rasa_sdk.interfaces import Tracker
from rasa_sdk.events import SlotSet
from actions.context_manager import DialogueContextManager

API_URL = "http://localhost:8000/chat"

# ======================================================
# CONFIGURATION FLAGS (KONTROL FALLBACK & FILTER)
# ======================================================
ENABLE_FALLBACK_CATCHER = (
    False  # Mengaktifkan/menonaktifkan pemulihan Regex/Keyword dari raw text
)
ENABLE_NLU_FILTERS = (
    False  # Mengaktifkan/menonaktifkan filter angka budget kecil dan nomor list
)

# ======================================================
# EXTRACT ENTITIES MURNI (TANPA HARDCODED ONTOLOGY)
# ======================================================


def extract_entities(entities, text=None):
    preference_terms = []
    feature_entities = []
    body_entities = []
    powertrain_entities = []
    brand_entities = []
    transmission_entities = []
    hard_filter_entities = []
    negated_entities = []
    raw_budgets = []
    min_seat = None
    must_have_sunroof = False

    # Check if text contains numbered list markers (e.g. "1. ", "2. ")
    list_markers = []
    if text:
        list_markers = re.findall(r"(\d+)\.\s", text)

    for e in entities:
        value = str(e.get("value", "")).lower().strip()
        entity_type = e.get("entity")

        # 1. CEK ML ROLE
        is_negated = e.get("role") == "negated"
        if is_negated:
            negated_entities.append(value)
            continue

        # 2. FILTER NUMBERED LIST (Ignore markers like "1" in "1. bensin")
        if ENABLE_NLU_FILTERS and entity_type in ["min_seat", "budget"]:
            if value in list_markers:
                print(
                    f"[RASA ACTION] [FILTER] Mengabaikan '{value}' karena terdeteksi sebagai nomor urut list."
                )
                continue

        if entity_type == "preference":
            sub_values = re.split(r"[,;/]+", value)
            for sv in [v.strip() for v in sub_values if v.strip()]:
                if len(sv) > 1:
                    preference_terms.append(sv)

        elif entity_type == "feature":
            feature_entities.append(value)
            if any(kw in value for kw in ["sunroof", "moonroof", "panoramic"]):
                must_have_sunroof = True

        elif entity_type == "body_type":
            body_entities.append(value)
        elif entity_type == "powertrain":
            powertrain_entities.append(value)
        elif entity_type == "brand":
            brand_entities.append(value)
        elif entity_type == "transmission":
            transmission_entities.append(value)
        elif entity_type == "hard_filter":
            hard_filter_entities.append(value)

        elif entity_type == "min_seat":
            try:
                match = re.search(r"\d+", value)
                if match:
                    seat_val = int(match.group())
                    if 2 <= seat_val <= 8:
                        min_seat = seat_val
                        hard_filter_entities.append(f"{seat_val} seat")
                    else:
                        print(
                            f"[RASA ACTION] [FILTER] Seat {seat_val} di luar skala 2-8."
                        )
            except:
                pass

        elif entity_type == "budget":
            # Budget Guard: Abaikan angka kecil (< 20) kecuali ada unit "jt/juta"
            is_small = False
            if ENABLE_NLU_FILTERS:
                try:
                    numeric_part = re.search(r"[\d\.,]+", value)
                    if numeric_part:
                        num = float(numeric_part.group().replace(",", ""))
                        if num < 20 and not any(
                            kw in value
                            for kw in ["jt", "juta", "milyar", "miliar", "m"]
                        ):
                            is_small = True
                except:
                    pass

            if is_small:
                print(
                    f"[RASA ACTION] [FILTER] Mengabaikan budget mencurigakan '{value}' (terlalu kecil)."
                )
            else:
                raw_budgets.append(value)

    # 3. FALLBACK CATCHER DARI RAW TEXT
    # Jika model NLU gagal mengenali entitas "seat" secara penuh, kita bantu dengan regex mentah
    if ENABLE_FALLBACK_CATCHER and text:
        txt_lower = text.lower()
        if min_seat is None:
            seat_match = re.search(r"(\d+)\s*(seat|kursi|penumpang)", txt_lower)
            if seat_match:
                try:
                    seat_val = int(seat_match.group(1))
                    if 2 <= seat_val <= 8:
                        min_seat = seat_val
                        hard_filter_entities.append(f"{seat_val} seat")
                        print(
                            f"[RASA ACTION] [FALLBACK DETECTED] Memulihkan entitas min_seat: {seat_val} dari raw text."
                        )
                except:
                    pass

        # 4. FALLBACK CATCHER UNTUK TARGET PREFERENSI
        # Jika NLP meleset dari term krusial, kita tangkap teks aslinya
        critical_keywords = [
            "keluarga",
            "nyaman",
            "irit",
            "hemat",
            "kencang",
            "sporty",
            "tangguh",
            "offroad",
            "mewah",
            "murah",
        ]
        for kw in critical_keywords:
            if kw in txt_lower and kw not in preference_terms:
                preference_terms.append(kw)
                print(
                    f"[RASA ACTION] [FALLBACK DETECTED] Memulihkan preference term: '{kw}' dari raw text."
                )

        # 5. FALLBACK NEGATION CATCHER (SAFETY NET FOR ROLES)
        negatable_terms = {
            "transmission": [
                "matic",
                "manual",
                "cvt",
                "dct",
                "amt",
                "single speed",
                "dht",
            ],
            "powertrain": [
                "hybrid",
                "bensin",
                "diesel",
                "listrik",
                "ev",
                "bev",
                "phev",
                "hev",
            ],
            "brand": [
                "toyota",
                "honda",
                "suzuki",
                "mitsubishi",
                "nissan",
                "mazda",
                "hyundai",
                "kia",
                "wuling",
                "chery",
                "bmw",
                "mercedes",
            ],
            "body_type": ["suv", "mpv", "sedan", "hatchback", "coupe", "wagon"],
        }

        negation_patterns = [
            r"jangan\s+(?:yang\s+)?{}",
            r"tidak\s+(?:mau|suka|perlu)?\s+{}",
            r"bukan\s+{}",
            r"ga\s+mau\s+{}",
            r"gak\s+mau\s+{}",
            r"enggan\s+{}",
            r"anti\s+{}",
            r"skip\s+{}",
            r"exclude\s+{}",
            r"hindari\s+(?:yang\s+)?{}",
        ]

        for category, terms in negatable_terms.items():
            for term in terms:
                for pat in negation_patterns:
                    pattern = pat.format(re.escape(term))
                    if re.search(pattern, txt_lower):
                        if term not in negated_entities:
                            negated_entities.append(term)
                            print(
                                f"[RASA ACTION] [NEGATION FALLBACK] Menangkap negasi untuk '{term}' (kategori: {category}) dari raw text."
                            )

        # 6. FALLBACK POSITIVE CATCHER FOR RECOGNIZED DICTIONARIES
        # Jika NLU meleset tetapi term ada di kamus dan tidak dinegasikan, kita masukkan sebagai entitas positif
        positive_fallback_terms = {
            "transmission": (
                transmission_entities,
                ["matic", "manual", "cvt", "dct", "amt", "single speed", "dht"],
            ),
            "powertrain": (
                powertrain_entities,
                ["hybrid", "bensin", "diesel", "listrik", "ev", "bev", "phev", "hev"],
            ),
            "brand": (
                brand_entities,
                [
                    "toyota",
                    "honda",
                    "suzuki",
                    "mitsubishi",
                    "nissan",
                    "mazda",
                    "hyundai",
                    "kia",
                    "wuling",
                    "chery",
                    "bmw",
                    "mercedes",
                ],
            ),
            "body_type": (
                body_entities,
                ["suv", "mpv", "sedan", "hatchback", "coupe", "wagon"],
            ),
        }
        for category, (entity_list, terms) in positive_fallback_terms.items():
            for term in terms:
                pattern = r"\b" + re.escape(term) + r"\b"
                if re.search(pattern, txt_lower):
                    if term not in negated_entities and term not in entity_list:
                        entity_list.append(term)
                        print(
                            f"[RASA ACTION] [POSITIVE FALLBACK] Memulihkan {category}: '{term}' dari raw text."
                        )

    # Bersihkan entitas positif yang ternyata terdeteksi sebagai negated di fallback
    body_entities = [x for x in body_entities if x not in negated_entities]
    powertrain_entities = [x for x in powertrain_entities if x not in negated_entities]
    brand_entities = [x for x in brand_entities if x not in negated_entities]
    transmission_entities = [
        x for x in transmission_entities if x not in negated_entities
    ]

    return {
        "preference_terms": preference_terms,
        "feature_entities": feature_entities,
        "body_entities": body_entities,
        "powertrain_entities": powertrain_entities,
        "brand_entities": brand_entities,
        "transmission_entities": transmission_entities,
        "hard_filter_entities": hard_filter_entities,
        "negated_entities": negated_entities,
        "raw_budgets": raw_budgets,
        "min_seat": min_seat,
        "must_have_sunroof": must_have_sunroof,
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

        # 1. REDIRECT LOOKALIKE / K-MEANS ROUTE
        # Jika pesan mengandung entitas target_car, intent adalah ask_similar_car,
        # atau text mengandung kata kunci kemiripan (look-alike),
        # segera alihkan seluruh proses ke ActionFindLookalike untuk menghindari jalur VIKOR.
        target_car_entity = None
        for e in entities:
            if e.get("entity") == "target_car":
                target_car_entity = e.get("value")
                break

        import re

        similar_keywords = [
            "alternatif",
            "mirip",
            "sekelas",
            "sejenis",
            "setara",
            "kompetitor",
            "saingan",
            "setipe",
            "kayak",
        ]
        pattern = r"\b(" + "|".join(re.escape(w) for w in similar_keywords) + r")\b"
        has_similar_keyword = bool(re.search(pattern, text.lower()))

        if (
            intent_name == "ask_similar_car"
            or target_car_entity is not None
            or has_similar_keyword
        ):
            print(
                f"[RASA ACTION] [REDIRECT] Mengalihkan ke ActionFindLookalike karena target_car '{target_car_entity}', intent '{intent_name}', or keyword terdeteksi."
            )
            return ActionFindLookalike().run(dispatcher, tracker, domain)

        # Pendelegasian Out Of Scope ke fallback policy / utter_default
        if intent_name == "out_of_scope":
            print(
                f"[RASA ACTION] [OUT-OF-SCOPE] TERDETEKSI PESAN OUT-OF-DOMAIN: '{text}'. Mengeksekusi fallback action."
            )
            dispatcher.utter_message(response="utter_default")
            return []

        parsed = extract_entities(entities, text=text)
        new_query = intent_name == "start_search"

        if new_query:
            print(
                "[RASA ACTION] [RESET] NEW QUERY DETECTED -> Mereset seluruh konteks sesi."
            )
            prev_min_budget = None
            prev_max_budget = None
        else:
            print(
                "[RASA ACTION] [CONTEXT] Menggabungkan Kriteria dengan memori konteks melalui OOP."
            )
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
            + merged_context["transmission_entities"]
            + merged_context["hard_filter_entities"]
            + merged_context["preference_terms"]
        )

        print(
            f"[RASA ACTION] Merged context: preferences={merged_context['preference_terms']}, entities={entities_combined}"
        )

        payload = {
            "user_message": text,
            "preference_terms": merged_context["preference_terms"],
            "need_terms": [],
            "weight_input": {},
            "entities": entities_combined,
            "negated_terms": merged_context["negated_terms"],
            "raw_budgets": merged_context["raw_budgets"],
            "min_budget": prev_min_budget,
            "max_budget": prev_max_budget,
            "min_seat": merged_context.get("min_seat"),
            "must_have_sunroof": merged_context.get("must_have_sunroof", False),
        }

        print(f"[RASA ACTION] Meminta routing/state dari backend...")
        try:
            ui_resp = requests.post(
                API_URL,
                json=payload,
            )
            ui_resp.raise_for_status()
            ui_data = ui_resp.json()

            if ui_data.get("action") == "ask_weights":
                returned_payload = ui_data.get("payload", {})
                payload["profile_display_name"] = returned_payload.get(
                    "profile_display_name", "Personalized"
                )
                payload["base_weight_profile"] = returned_payload.get(
                    "base_weight_profile", {}
                )
            else:
                payload["base_weight_profile"] = {}

            print(
                f"[RASA ACTION] State response received: {payload.get('profile_display_name')}"
            )
        except Exception as e:
            print(f"[RASA ACTION] [ERROR] Gagal memanggil /chat API: {e}")
            payload["base_weight_profile"] = {}

        # ─────────────────────────────────────────────────────────────────────────────
        # PERBAIKAN: Handle Budget-Only Query
        #
        # LOGIKA LAMA (bermasalah):
        #   Kondisi hanya cek `not new_query` → jika user follow-up dengan jawaban
        #   preferensi yang panjang (misal "irit dan nyaman kalau bisa canggih"),
        #   intent masih bisa terklasifikasi sebagai ask_recommendation bukan
        #   choose_preference, sehingga has_preferences bisa tetap kosong karena
        #   entity tidak ter-extract sempurna.
        #
        # LOGIKA BARU:
        #   Cek apakah ada budget yang tersimpan di slot (dari turn sebelumnya).
        #   Jika ada budget lama + preferensi baru terdeteksi → langsung proses.
        #   Jika hanya budget baru tanpa preferensi → minta preferensi.
        #   Ini memastikan alur 2-turn tetap berjalan meski entity extraction
        #   tidak sempurna di turn pertama.
        # ─────────────────────────────────────────────────────────────────────────────

        has_preferences = any(
            [
                merged_context["preference_terms"],
                merged_context["feature_entities"],
                merged_context["brand_entities"],
                merged_context["powertrain_entities"],
                merged_context["body_entities"],
                merged_context["hard_filter_entities"],
            ]
        )
        has_budget = bool(merged_context["raw_budgets"])

        # Cek apakah ada budget yang sudah tersimpan dari turn sebelumnya
        has_previous_budget = bool(
            tracker.get_slot("raw_budgets")
            or tracker.get_slot("min_budget")
            or tracker.get_slot("max_budget")
        )

        global_budget_present = has_budget or has_previous_budget

        # SKENARIO 0: User tidak menyebut budget sama sekali
        if not global_budget_present:
            print(
                "[RASA ACTION] [MISSING BUDGET] User lupa menyebutkan budget. Meminta budget."
            )
            dispatcher.utter_message(response="utter_ask_budget")
            return [
                SlotSet("preference", merged_context["preference_terms"]),
                SlotSet("feature", merged_context["feature_entities"]),
                SlotSet("brand", merged_context["brand_entities"]),
                SlotSet("powertrain", merged_context["powertrain_entities"]),
                SlotSet("transmission", merged_context["transmission_entities"]),
                SlotSet("body_type", merged_context["body_entities"]),
                SlotSet("hard_filter", merged_context["hard_filter_entities"]),
                SlotSet("min_seat", merged_context.get("min_seat")),
                SlotSet(
                    "must_have_sunroof", merged_context.get("must_have_sunroof", False)
                ),
                SlotSet("negated_terms", merged_context["negated_terms"]),
            ]

        # SKENARIO 1: User hanya sebut budget, belum ada preferensi sama sekali di context
        if has_budget and not has_preferences and not new_query:
            print(
                "[RASA ACTION] [FOLLOW-UP] User hanya menyebut budget. Meminta preferensi tambahan."
            )
            dispatcher.utter_message(response="utter_ask_initial_preference")
            return [
                SlotSet("raw_budgets", merged_context["raw_budgets"]),
            ]

        # SKENARIO 2: Cek apakah butuh Refinement (Bahan bakar, Kursi, Fitur)
        # Dilakukan jika (Has Budget + Has Prefs) tapi info teknis masih sangat minim
        is_refined = tracker.get_slot("refinement_stage")

        # Gunakan merged_context (data terbaru) untuk cek ketersediaan informasi teknis
        has_powertrain = bool(merged_context.get("powertrain_entities"))
        has_feature = bool(merged_context.get("feature_entities"))

        # Cek ketersediaan info kursi dari berbagai kemungkinan (NLU min_seat, entitas filter, memori, DAN raw text)
        has_seat_in_filters = any(
            "seat" in str(x).lower() or "kursi" in str(x).lower()
            for x in merged_context.get("hard_filter_entities", [])
        )
        has_seat_in_prefs = any(
            "seat" in str(x).lower() or "kursi" in str(x).lower()
            for x in merged_context.get("preference_terms", [])
        )
        has_seat_in_text = (
            any(w in text.lower() for w in ["seat", "kursi", "penumpang"])
            if text
            else False
        )

        has_seat = (
            bool(merged_context.get("min_seat"))
            or bool(tracker.get_slot("min_seat"))
            or has_seat_in_filters
            or has_seat_in_prefs
            or has_seat_in_text
        )

        needs_refinement = not (has_powertrain or has_feature or has_seat)

        if (
            has_budget
            and has_preferences
            and not is_refined
            and needs_refinement
            and not new_query
        ):
            print(
                "[RASA ACTION] [REFINEMENT] Mencoba melengkapi data (Bahan bakar, Kursi, Fitur)."
            )
            dispatcher.utter_message(response="utter_ask_refinement")
            return [
                SlotSet("preference", merged_context["preference_terms"]),
                SlotSet("raw_budgets", merged_context["raw_budgets"]),
                SlotSet("refinement_stage", True),
            ]

        # ─────────────────────────────────────────────────────────────────────────────
        # PERBAIKAN: Handle Refinement Skip
        #
        # Jika user sudah pernah ditanya refinement (is_refined=True) tapi menjawab
        # tanpa entity teknis baru (misal: "tidak ada", "langsung aja", "cukup"),
        # maka langsung lanjut ke pencarian tanpa meminta data lagi.
        # ─────────────────────────────────────────────────────────────────────────────
        if is_refined and needs_refinement:
            print(
                "[RASA ACTION] [REFINEMENT SKIP] User melewati tahap refinement "
                f"(jawaban: '{text}'). Langsung lanjut ke pencarian."
            )

        # SKENARIO 3: User baru memberikan preferensi sebagai follow-up dari budget sebelumnya
        # (has_previous_budget = True, has_preferences = True)
        if has_previous_budget and has_preferences:
            print(
                f"[RASA ACTION] [FOLLOW-UP RESOLVED] Budget dari sesi sebelumnya ditemukan + preferensi baru."
            )

        if new_query:
            print(
                f"[RASA ACTION] [NEW QUERY] Meminta input bobot manual dari frontend."
            )
            dispatcher.utter_message(
                text="Silakan atur bobot kriteria yang paling penting menurut Anda (misal: Performa, Irit, Kenyamanan).",
                custom={"action": "ask_weights", "payload": payload},
            )
        else:
            print(
                f"[RASA ACTION] [REFINEMENT] Langsung mencari mobil dengan payload: {payload}"
            )
            dispatcher.utter_message(
                text="Baik, kriteria pencarian sedang saya sesuaikan...",
                custom={"action": "search_cars", "payload": payload},
            )

        print("[RASA ACTION] Selesai memproses pesan, menunggu respon.")
        print("==================================================")

        return [
            SlotSet("preference", merged_context["preference_terms"]),
            SlotSet("feature", merged_context["feature_entities"]),
            SlotSet("brand", merged_context["brand_entities"]),
            SlotSet("powertrain", merged_context["powertrain_entities"]),
            SlotSet("transmission", merged_context["transmission_entities"]),
            SlotSet("body_type", merged_context["body_entities"]),
            SlotSet("hard_filter", merged_context["hard_filter_entities"]),
            SlotSet("raw_budgets", merged_context["raw_budgets"]),
            SlotSet("min_seat", merged_context.get("min_seat")),
            SlotSet(
                "must_have_sunroof", merged_context.get("must_have_sunroof", False)
            ),
            SlotSet("negated_terms", merged_context["negated_terms"]),
            SlotSet(
                "refinement_stage",
                False if new_query else tracker.get_slot("refinement_stage"),
            ),
            SlotSet(
                "target_car", None
            ),  # Reset target_car slot agar tidak bocor ke pencarian VIKOR berikutnya
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
                (tracker.get_slot("feature") or [])
                + (tracker.get_slot("brand") or [])
                + (tracker.get_slot("powertrain") or [])
                + (tracker.get_slot("body_type") or [])
                + (tracker.get_slot("hard_filter") or [])
            ),
            "min_seat": tracker.get_slot("min_seat"),
            "must_have_sunroof": tracker.get_slot("must_have_sunroof"),
            "min_budget": tracker.get_slot("min_budget"),
            "max_budget": tracker.get_slot("max_budget"),
            "previous_max_budget": prev_max_budget,
            "raw_budgets": parsed["raw_budgets"],
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
                    dispatcher.utter_message(
                        text="Berapa budget baru yang ingin kamu bandingkan?"
                    )
                    return []

        print(f"[RASA ACTION] 📊 Comparing budget payload: {payload}")

        try:
            response = requests.post(API_URL, json=payload)
            response.raise_for_status()
            data = response.json()

            cars = data.get("recommendations", [])
            comparison_insight = data.get("comparison_insight")

            if not cars:
                dispatcher.utter_message(
                    text="Maaf, saya tidak menemukan mobil yang cocok dengan budget baru tersebut."
                )
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
            dispatcher.utter_message(
                text="Maaf, terjadi kendala saat memproses perbandingan budget."
            )

        return []


class ActionFindLookalike(Action):

    def name(self):
        return "action_find_lookalike"

    def run(self, dispatcher, tracker, domain):
        text = tracker.latest_message.get("text", "")
        entities = tracker.latest_message.get("entities", [])

        # Prioritize entity from latest message over slot
        target_car = None
        for e in entities:
            if e.get("entity") == "target_car":
                target_car = e.get("value")
                break

        if not target_car:
            target_car = tracker.get_slot("target_car")

        # Extract from text as fallback if still none
        if not target_car:
            cleaned_text = text.lower()

            # Check if this is a Rasa slash command (payload starting with /)
            if cleaned_text.startswith("/"):
                try:
                    import json

                    json_str = cleaned_text[
                        cleaned_text.find("{") : cleaned_text.rfind("}") + 1
                    ]
                    if json_str:
                        payload_dict = json.loads(json_str)
                        target_car = payload_dict.get("target_car")
                except Exception as ex:
                    print(f"[RASA ACTION] Gagal parse JSON payload: {ex}")

            if not target_car:
                import re

                words_to_remove = [
                    "alternatif",
                    "mirip",
                    "sekelas",
                    "sejenis",
                    "setara",
                    "kompetitor",
                    "saingan",
                    "setipe",
                    "kayak",
                    "selain",
                    "dong",
                    "sih",
                    "deh",
                    "ya",
                    "aja",
                    "saja",
                    "mobil",
                    "yang",
                    "cari",
                ]
                pattern = (
                    r"\b(" + "|".join(re.escape(w) for w in words_to_remove) + r")\b"
                )
                cleaned_text = re.sub(pattern, "", cleaned_text)
                target_car = re.sub(r"\s+", " ", cleaned_text).strip()

        if not target_car:
            dispatcher.utter_message(text="Mobil apa yang ingin dicari alternatifnya?")
            return []

        if isinstance(target_car, list):
            target_car = target_car[0]

        print(f"[RASA ACTION] Mencari lookalike untuk: {target_car}")

        try:
            # Panggil endpoint /chat (Sentral Router)
            chat_resp = requests.post(
                "http://localhost:8000/chat", json={"target_car": target_car}
            )
            chat_resp.raise_for_status()
            data = chat_resp.json()

            if "error" in data:
                dispatcher.utter_message(text=data["error"])
                return []

            if data.get("action") == "disambiguate_car":
                print(
                    f"[RASA ACTION] Ambiguous target '{target_car}'. Triggering popup."
                )
                dispatcher.utter_message(
                    text=f"Ada beberapa varian untuk '{target_car}'. Silakan pilih yang mana:",
                    custom={
                        "action": "disambiguate_car",
                        "matches": data["matches"],
                        "query": data["query"],
                    },
                )
                return [SlotSet("target_car", target_car)]

            if "recommendations" in data:
                cars = data["recommendations"]
                if not cars:
                    dispatcher.utter_message(
                        text="Maaf, saya tidak menemukan mobil yang sekelas."
                    )
                    return []

                dispatcher.utter_message(
                    text=f"Sip! Berdasarkan K-Means Clustering, ini 5 mobil yang setara dengan pencarian Anda:",
                    custom={
                        "recommendations": cars,
                        "constraint_report": data.get("constraint_report"),
                    },
                )

        except Exception as e:
            print(f"[RASA ACTION] Error calling chat backend: {e}")
            dispatcher.utter_message(
                text="Maaf, terjadi kesalahan teknis pada sistem rekomendasi."
            )

        return [SlotSet("target_car", target_car)]
