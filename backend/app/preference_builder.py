# backend/app/preference_builder.py

from app.feature_ontology import (
    PREFERENCE_INDEX_MAP,
    BODY_TYPE_MAP,
    POWERTRAIN_MAP,
    FEATURE_CONSTRAINT_MAP,
    HARD_FILTER_MAP,
    BRAND_MAP,
    PREFERENCE_CLUSTER_MAP
)


# ======================================================
# BUILD WEIGHT DICTIONARY
# ======================================================

def build_weight_dict(preference_terms, weight_input):

    weight_dict = {}

    for term in set(preference_terms):

        if term not in PREFERENCE_INDEX_MAP:
            continue

        index_name = PREFERENCE_INDEX_MAP[term]

        weight = float(weight_input.get(term, 0))

        weight_dict[index_name] = max(
            weight,
            weight_dict.get(index_name, 0)
        )

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

    params["brand"] = extract_brand(entities)

    params["feature_constraints"] = build_feature_constraints(
        entities
    )

    params.update(
        build_hard_filters(entities)
    )

    return params
