# chatbot-rekomendasi-mobil/backend/clustering/agglomerative.py

import pandas as pd
import numpy as np

from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score


# ======================================================
# FEATURES UNTUK CLUSTERING (STRUKTURAL & ARSITEKTURAL)
# ======================================================

CLUSTER_FEATURES = [
    "INDEX_POWER",      # Tenaga
    "INDEX_HANDLING",   # Kelincahan/Aerodinamika
    "INDEX_EFFICIENCY", # Keiritan
    "INDEX_SPACE",      # Kapasitas/Ukuran
    "INDEX_OFFROAD",    # Ketangguhan
    "INDEX_PRICE"       # Level Harga
]

# ======================================================
# FEATURE MATRIX BUILDER
# ======================================================

def build_feature_matrix(df):
    features = [c for c in CLUSTER_FEATURES if c in df.columns]

    if len(features) == 0:
        raise ValueError("Tidak ada fitur clustering ditemukan")

    X = df[features].fillna(0).values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return X_scaled, features


# ======================================================
# AUTO CLUSTER DETECTION
# ======================================================

def detect_optimal_clusters(X, min_k=4, max_k=8):
    best_score = -1
    best_k = min_k

    for k in range(min_k, max_k + 1):
        try:
            model = AgglomerativeClustering(
                n_clusters=k,
                linkage="ward"
            )
            labels = model.fit_predict(X)
            score = silhouette_score(X, labels)

            if score > best_score:
                best_score = score
                best_k = k
        except Exception:
            continue

    return best_k

# ======================================================
# CLUSTER PROFILING (SEMANTIC MAPPING)
# ======================================================

def assign_cluster_profiles(df):

    features = [c for c in CLUSTER_FEATURES if c in df.columns]

    cluster_profiles = df.groupby("CLUSTER_ID")[features].mean()

    score_table = []

    for cluster_id, p in cluster_profiles.iterrows():

        scores = {}

        # City Car: Irit, Kecil, Murah
        scores["City Car"] = (
            p["INDEX_EFFICIENCY"] +
            p["INDEX_PRICE"] -
            p["INDEX_SPACE"]
        )

        # Family Car: Luas, Nyaman (proxy by Space), Aman (proxy by Power/Handling Balance)
        scores["Family Car"] = (
            p["INDEX_SPACE"] +
            p["INDEX_HANDLING"]
        )

        # Tough SUV / Offroad: GC Tinggi, Tenaga Oke
        scores["Offroad"] = (
            p["INDEX_OFFROAD"] +
            p["INDEX_POWER"]
        )

        # Performance / Sports: Tenaga Tinggi, Handling Tinggi (Ceper)
        scores["Performance"] = (
            p["INDEX_POWER"] +
            p["INDEX_HANDLING"]
        )

        # Luxury / Premium: Mahal, Tenaga Tinggi, Kabin Luas
        scores["Luxury"] = (
            p["INDEX_POWER"] +
            p["INDEX_SPACE"] -
            p.get("INDEX_PRICE", 0) # Minus karena price index tinggi = murah, premium = mahal (low score)
        )

        score_table.append((cluster_id, scores))

    labels = ["City Car","Family Car","Offroad","Performance","Luxury"]

    cluster_labels = {}
    used_clusters = set()

    for label in labels:

        best_cluster = None
        best_score = -np.inf

        for cid, scores in score_table:

            if cid in used_clusters:
                continue

            if scores[label] > best_score:
                best_score = scores[label]
                best_cluster = cid

        if best_cluster is not None:
            cluster_labels[best_cluster] = label
            used_clusters.add(best_cluster)

    df["CLUSTER_NAME"] = df["CLUSTER_ID"].map(cluster_labels).fillna("General")

    return df, cluster_labels

# ======================================================
# MAIN CLUSTERING FUNCTION
# ======================================================

def perform_clustering(df):
    X, features = build_feature_matrix(df)

    # Biarkan algoritma menentukan K terbaik untuk sebaran yang lebih merata
    n_clusters = detect_optimal_clusters(X)
    print(f"[CLUSTERING] Optimal K detected: {n_clusters}")

    model = AgglomerativeClustering(
        n_clusters=n_clusters,
        linkage="ward"
    )

    labels = model.fit_predict(X)

    df = df.copy()
    df["CLUSTER_ID"] = labels

    # Terapkan penamaan cluster otomatis
    df, profile_dict = assign_cluster_profiles(df)
    
    print("[CLUSTERING] Karakteristik Otomatis Cluster yang Terbentuk:")
    for cid, cname in profile_dict.items():
        print(f"  - Cluster {cid}: {cname}")

    return df