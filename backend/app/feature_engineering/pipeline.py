# backend/app/feature engineering/pipeline.py

from .preprocessing import (
    encode_granular_features,
    merge_product_lifecycle_safe,
    merge_brand_strength,
    add_derived_features,
    clean_numeric_columns
)
from .scoring import calculate_indices


def generate_feature_dataset(df, wholesales, retail):
    """
    Pipeline utama feature engineering.

    Args:
        df        : dataset mobil utama (spesifikasi)
        wholesales: data wholesale per BRAND+MODEL+VARIAN
                    -> digunakan untuk INDEX_LIFECYCLE_SAFE
        retail    : data retail per BRAND (agregat bulanan)
                    -> digunakan untuk INDEX_BRAND_STRENGTH
    """

    df = clean_numeric_columns(df)

    df = encode_granular_features(df)

    # Dua metrik bisnis terstruktur dari data historis
    # 1. Wholesale: Rasio Tren Supply (Discontinue-Safe Proxy)
    df = merge_product_lifecycle_safe(df, wholesales)

    # 2. Retail: Agregat Market Share Aktual (Brand Ecosystem Proxy)
    df = merge_brand_strength(df, retail)

    df = add_derived_features(df)

    df = calculate_indices(df)

    return df