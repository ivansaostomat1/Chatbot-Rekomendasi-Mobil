# backend/app/preference_builder.py

from app.feature_ontology import (
    PREFERENCE_INDEX_MAP,
    BODY_TYPE_MAP,
    POWERTRAIN_MAP,
    DRIVETRAIN_MAP,
    FEATURE_CONSTRAINT_MAP,
    HARD_FILTER_MAP,
    BRAND_MAP,
    PREFERENCE_CLUSTER_MAP,
    CLUSTER_PROFILES,
    GLOBAL_DEFAULT_PROFILE
)


# ======================================================
# BUILD WEIGHT DICTIONARY
# ======================================================

# Bobot default yang diberikan ke sebuah index jika NLU mendeteksi preference term
# namun user belum menyetel bobot manual (via slider di frontend).
# Ini menggantikan logika boost yang sebelumnya ada di actions.py (Rasa).
NLP_DEFAULT_BOOST = 8.0

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

        for index_name in indices:
            weight_dict[index_name] = max(
                weight,
                weight_dict.get(index_name, 0)
            )
            print(f"  ⚙️ [BUILD_WEIGHT] '{term}' → {index_name} = {weight} ({source})")

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

def extract_cluster(preference_terms):

    clusters = []

    for term in preference_terms:

        term = term.lower()

        if term in PREFERENCE_CLUSTER_MAP:
            clusters.append(PREFERENCE_CLUSTER_MAP[term])

    if not clusters:
        return None

    # ambil cluster yang paling sering muncul
    return max(set(clusters), key=clusters.count)

def get_initial_ui_profile(preference_terms, need_terms=[], entities=[]):
    """
    Membangun profil bobot awal untuk UI sliders (ask_weights) 
    berdasarkan seluruh entitas yang terdeteksi (preferences, needs, features).
    """
    # Merge all terms for maximum context coverage
    all_terms = preference_terms + need_terms + entities
    
    cluster_name = extract_cluster(all_terms) or "Global"
    
    # Load base profile
    base_profile = dict(CLUSTER_PROFILES.get(cluster_name, GLOBAL_DEFAULT_PROFILE))
    
    # Boost based on all detected terms related to preference indices (NLP_DEFAULT_BOOST = 8.0)
    # Ini memberikan kesan "Chatbot mengerti Anda" saat slider pertama kali muncul.
    for term in all_terms:
        if term in PREFERENCE_INDEX_MAP:
            indices = PREFERENCE_INDEX_MAP[term]
            if isinstance(indices, str):
                indices = [indices]
            for idx in indices:
                # Masukkan boost jika lebih tinggi dari base profile
                base_profile[idx] = max(base_profile.get(idx, 0), 8.0)
                
    return cluster_name, base_profile

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
                
        # Dynamic Seat Parsing from Safety Net
        if "seat" in text or "penumpang" in text or "kursi" in text:
            import re
            nums = re.findall(r'\d+', text)
            if nums:
                filters["min_seat"] = int(nums[0])

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

    params["cluster_name"] = extract_cluster(preference_terms)

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
