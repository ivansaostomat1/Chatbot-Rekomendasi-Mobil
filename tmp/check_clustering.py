# /tmp/check_clustering.py
import sys
import os
import numpy as np
import pandas as pd

# Add backend to path
sys.path.append(os.path.abspath('backend'))

from app.feature_engineering.preprocessing import clean_numeric_columns, encode_granular_features, add_derived_features, merge_popularity
from app.feature_engineering.scoring import calculate_indices
from clustering.agglomerative import perform_clustering

# Load data
try:
    df = pd.read_csv('backend/data/mobil.csv')
    wholesales = pd.read_csv('backend/data/wholesales.csv')

    # Preprocess
    df = clean_numeric_columns(df)
    df = encode_granular_features(df)
    df = merge_popularity(df, wholesales)
    df = add_derived_features(df)

    # Calculate new indices
    df = calculate_indices(df)

    # Perform clustering
    df = perform_clustering(df)

    # Print summary
    print("\n" + "="*50)
    print("CLUSTER SUMMARY")
    print("="*50)
    summary = df.groupby(["CLUSTER_ID", "CLUSTER_NAME"]).size().reset_index(name='count')
    print(summary)

    print("\nSample Cars per Cluster:")
    for cid in sorted(df['CLUSTER_ID'].unique()):
        subset = df[df['CLUSTER_ID']==cid]
        cname = subset['CLUSTER_NAME'].iloc[0]
        samples = subset[['BRAND', 'MODEL']].drop_duplicates().head(5)
        sample_str = ", ".join([f"{r['BRAND']} {r['MODEL']}" for _, r in samples.iterrows()])
        print(f"- Cluster {cid} ({cname}): {sample_str}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
