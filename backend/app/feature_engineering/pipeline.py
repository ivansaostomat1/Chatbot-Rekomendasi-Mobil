# backend/app/feature engineering/pipeline.py

from .preprocessing import (
    encode_granular_features,
    merge_popularity,
    add_derived_features,
    clean_numeric_columns
)
from .scoring import calculate_indices


def generate_feature_dataset(df, wholesales):

    df = clean_numeric_columns(df)

    df = encode_granular_features(df)

    df = merge_popularity(df, wholesales)

    df = add_derived_features(df)

    df = calculate_indices(df)

    return df