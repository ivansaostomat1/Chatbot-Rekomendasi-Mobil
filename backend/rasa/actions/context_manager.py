class DialogueContextManager:
    """
    Mengelola Deduplikasi, Akumulasi State, dan Filter Negasi
    untuk Rasa NLP Action Server.
    """

    def __init__(self, tracker, new_parsed_entities, reset_context=False):
        self.tracker = tracker
        self.new_parsed = new_parsed_entities
        self.reset_context = reset_context
        self.negated = self.new_parsed.get("negated_entities", [])
        
        print("\n" + "="*50)
        print("CORE [CONTEXT MANAGER] INISIALISASI OOP STATE TRACKER")
        print("="*50)
        print(f" - Reset Context (New Query)? : {reset_context}")
        print(f" - Negated Entities (To Drop) : {self.new_parsed.get('negated_entities', [])}")
        print(f" - New Parsed Entities        : {new_parsed_entities}")
        
        # Accumulate with previous negations unless reset
        prev_negated = self._get_prev("negated_terms")
        self.negated = self._unique_clean(self.new_parsed.get("negated_entities", []) + prev_negated)
        print(f" - Total Negated Context      : {self.negated}")
        
    def _get_prev(self, slot_name):
        if self.reset_context:
            return []
        val = self.tracker.get_slot(slot_name)
        if val is None:
            return []
        if isinstance(val, list):
            return val
        return [val]

    def _unique_clean(self, lst):
        """Standard deduplication"""
        return list(set([str(x).strip().lower() for x in lst if x]))

    def _merge_and_strip(self, current, prev, field_name=""):
        """Gabungkan entity lama dan baru, lalu hilangkan entitas 'negated'"""
        combined = self._unique_clean(current + prev)
        final_list = [x for x in combined if x not in self.negated]
        
        # Logging yang sangat detail untuk membantu debug/skripsi
        if current or prev:
            print(f"  [{field_name.upper()}]")
            print(f"   |- P : {prev}")
            print(f"   |- L : {current}")
            print(f"   |- - : {[x for x in combined if x in self.negated]}")
            print(f"   \- R : {final_list}")
            
        return final_list

    def get_merged_context(self):
        """Memproses semua entitas secara OOP, mengembalikan dictionary slot yang siap diekstrak."""
        print("SYNC [CONTEXT MANAGER] MENGGABUNGKAN MEMORI (P=Previous, L=Latest, -=Removed, R=Result)...")
        result = {
            "preference_terms": self._merge_and_strip(self.new_parsed["preference_terms"], self._get_prev("preference"), "PREFERENCES"),
            "feature_entities": self._merge_and_strip(self.new_parsed["feature_entities"], self._get_prev("feature"), "FEATURES"),
            "brand_entities": self._merge_and_strip(self.new_parsed["brand_entities"], self._get_prev("brand"), "BRANDS"),
            "powertrain_entities": self._merge_and_strip(self.new_parsed["powertrain_entities"], self._get_prev("powertrain"), "POWERTRAIN"),
            "body_entities": self._merge_and_strip(self.new_parsed["body_entities"], self._get_prev("body_type"), "BODY_TYPE"),
            "hard_filter_entities": self._merge_and_strip(self.new_parsed["hard_filter_entities"], self._get_prev("hard_filter"), "HARD_FILTERS"),
            
            # Budget tidak di-_merge (jangan digabungkan), tapi jika baru di-set, timpa yang lama
            "raw_budgets": self.new_parsed.get("raw_budgets") or self._get_prev("raw_budgets"),
            
            # Technical Constraints
            "min_seat": self.new_parsed.get("min_seat") or self.tracker.get_slot("min_seat"),
            "must_have_sunroof": self.new_parsed.get("must_have_sunroof") or self.tracker.get_slot("must_have_sunroof"),

            # Negated terms yang sudah diakumulasikan dan di-deduplikasi
            "negated_terms": self.negated
        }
        
        # Log budget memory behavior
        if result["raw_budgets"]:
            print(f"  [RAW_BUDGETS]")
            print(f"   |- P : {self._get_prev('raw_budgets')}")
            print(f"   |- L : {self.new_parsed.get('raw_budgets')}")
            print(f"   \- R : {result['raw_budgets']}")
            
        print("DONE [CONTEXT MANAGER] Selesai Menggabungkan Context!")
        print("="*50 + "\n")
        return result
