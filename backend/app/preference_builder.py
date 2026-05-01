# backend/app/preference_builder.py
from typing import List

from app.feature_ontology import (
    PREFERENCE_INDEX_MAP,
    BODY_TYPE_MAP,
    POWERTRAIN_MAP,
    DRIVETRAIN_MAP,
    FEATURE_CONSTRAINT_MAP,
    HARD_FILTER_MAP,
    BRAND_MAP,
    PREFERENCE_PROFILE_MAP,
    AHP_PROFILES,
    GLOBAL_DEFAULT_PROFILE
)
from .feature_engineering.preference_weight_map import (
    resolve_preference_weights,
    detect_profile_from_weights
)


# ======================================================
# BUILD WEIGHT DICTIONARY
# ======================================================

# Bobot default yang diberikan ke sebuah index jika NLU mendeteksi preference term
# namun user belum menyetel bobot manual (via slider di frontend).
# Ini menggantikan logika boost yang sebelumnya ada di actions.py (Rasa).
NLP_DEFAULT_BOOST = 8.0

# Mapping between Frontend Short Keys (UI) and Backend Criteria (VIKOR)
# UI_TO_INDEX_MAP moved to feature_ontology.py
from .feature_ontology import UI_TO_INDEX_MAP

def build_weight_dict(preference_terms, weight_input):

    weight_dict = {}

    for term in set(preference_terms):

        if term not in PREFERENCE_INDEX_MAP:
            continue

        indices = PREFERENCE_INDEX_MAP[term]
        
        # Pastikan indices adalah list (mendukung legacy string mapping juga)
        if isinstance(indices, str):
            indices = [indices]

        # Gunakan NLP_DEFAULT_BOOST jika user belum menyetel bobot manual untuk term ini.
        # NLP_DEFAULT_BOOST = suara "default" dari sistem NLU bahwa term ini penting.
        weight = float(weight_input.get(term, NLP_DEFAULT_BOOST))
        source = "manual" if term in weight_input else "NLP_DEFAULT_BOOST"

        for u_key in indices:
            index_name = UI_TO_INDEX_MAP.get(u_key, u_key)
            weight_dict[index_name] = max(
                weight,
                weight_dict.get(index_name, 0)
            )
            print(f"  [BUILD_WEIGHT] '{term}' --- {index_name} = {weight} ({source})")

    # Sesuai permintaan user: Value For Money (INDEX_PRICE) selalu maksimal (10)
    # Ini memastikan VIKOR selalu memprioritaskan balance kualitas vs harga yang kompetitif.
    weight_dict["INDEX_PRICE"] = 10.0

    return weight_dict

# ======================================================
# BUILD BODY TYPE
# ======================================================

def extract_body_type(entities):

    for e in entities:

        text = e.lower()

        if text in BODY_TYPE_MAP:
            return BODY_TYPE_MAP[text]

    return None


# ======================================================
# BUILD POWERTRAIN
# ======================================================

def extract_powertrain(entities):

    for e in entities:

        text = e.lower()

        if text in POWERTRAIN_MAP:
            return POWERTRAIN_MAP[text]

    return None


# ======================================================
# BUILD DRIVETRAIN
# ======================================================

def extract_drive_sys(entities):
    for e in entities:
        text = e.lower()
        if text in DRIVETRAIN_MAP:
            return DRIVETRAIN_MAP[text]
    return None


# ======================================================
# BUILD CLUSTER
# ======================================================

def extract_profile(all_terms: List[str]) -> List[str]:
    """
    Scientific profile detection based on aggregated weights from ALL terms 
    (preferences AND hard constraints like 'keluarga besar').
    """
    if not all_terms:
        return ["Global"]
        
    # Agregasi bobot dari semua terms (termasuk hard constraints)
    weights = resolve_preference_weights(all_terms)
    
    # Deteksi profile list dari profile bobot hasil agregasi
    profiles = detect_profile_from_weights(weights, preference_terms=all_terms)
    
    return profiles

def get_initial_ui_profile(preference_terms, need_terms=[], entities=[]):
    """
    Membangun profil bobot awal untuk UI sliders (ask_weights) 
    berdasarkan seluruh entitas yang terdeteksi (preferences, needs, features).
    """
    # Merge all terms for maximum context coverage
    all_terms = list(set(preference_terms + need_terms + entities))
    
    profiles = extract_profile(all_terms)
    primary_profile = profiles[0]
    
    # Load base profile dari primary profile (Internal keys)
    base_raw = dict(AHP_PROFILES.get(primary_profile, GLOBAL_DEFAULT_PROFILE))
    
    # Boost based on all detected terms related to preference indices (NLP_DEFAULT_BOOST = 8.0)
    for term in all_terms:
        if term in PREFERENCE_INDEX_MAP:
            indices = PREFERENCE_INDEX_MAP[term]
            if isinstance(indices, str):
                indices = [indices]
            for idx in indices:
                # Masukkan boost jika lebih tinggi dari base profile
                base_raw[idx] = max(base_raw.get(idx, 0), 8.0)
    
    # BRIDGE: Map Internal Keys -> UI Keys (INDEX_...)
    base_profile = {}
    for short_key, val in base_raw.items():
        ui_key = UI_TO_INDEX_MAP.get(short_key, short_key)
        base_profile[ui_key] = val
                
    return primary_profile, base_profile

# ======================================================
# BUILD FEATURE CONSTRAINTS
# ======================================================

def build_feature_constraints(entities):

    constraints = {}

    for e in entities:

        text = e.lower()

        if text in FEATURE_CONSTRAINT_MAP:

            col, val = FEATURE_CONSTRAINT_MAP[text]

            constraints[col] = max(val, constraints.get(col, 0))

    return constraints


# ======================================================
# BUILD HARD FILTERS
# ======================================================

def build_hard_filters(entities):

    filters = {}

    for e in entities:

        text = e.lower()

        if text in HARD_FILTER_MAP:

            for k, v in HARD_FILTER_MAP[text].items():
                filters[k] = v
                
        # Dynamic Seat Parsing from Safety Net (Scale 2-8 only)
        if "seat" in text or "penumpang" in text or "kursi" in text:
            import re
            nums = re.findall(r'\d+', text)
            if nums:
                val = int(nums[0])
                if 2 <= val <= 8:
                    filters["min_seat"] = val

    return filters

# ======================================================
# BUILD BRAND
# ======================================================

def extract_brand(entities):

    for e in entities:

        text = e.lower()

        if text in BRAND_MAP:
            return BRAND_MAP[text]

    return None
    
# ======================================================
# MAIN BUILDER
# ======================================================
def build_recommendation_params(
    preference_terms,
    weight_input,
    entities
):

    params = {}

    params["weight_dict"] = build_weight_dict(
        preference_terms,
        weight_input
    )

    # Broaden profile detection using ALL context
    all_context = list(set(preference_terms + entities))
    params["ahp_profile"] = extract_profile(all_context)

    params["body_type"] = extract_body_type(entities)

    params["powertrain"] = extract_powertrain(entities)

    params["drive_sys"] = extract_drive_sys(entities)

    params["brand"] = extract_brand(entities)

    params["feature_constraints"] = build_feature_constraints(
        entities
    )

    params.update(
        build_hard_filters(entities)
    )

    return params

