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
    GLOBAL_DEFAULT_WEIGHTS,
    UI_TO_INDEX_MAP
)
from .feature_engineering.preference_weight_map import (
    resolve_preference_weights
)


# ======================================================
# BUILD WEIGHT DICTIONARY
# ======================================================

# Bobot default yang diberikan ke sebuah index jika NLU mendeteksi preference term
# namun user belum menyetel bobot manual (via slider di frontend).
NLP_DEFAULT_BOOST = 8.0

def build_weight_dict(preference_terms, weight_input):

    weight_dict = {}

    for term in set(preference_terms):

        if term not in PREFERENCE_INDEX_MAP:
            continue

        indices = PREFERENCE_INDEX_MAP[term]
        
        # Pastikan indices adalah list
        if isinstance(indices, str):
            indices = [indices]

        # Gunakan NLP_DEFAULT_BOOST jika user belum menyetel bobot manual untuk term ini.
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
