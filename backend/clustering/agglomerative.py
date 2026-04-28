# chatbot-rekomendasi-mobil/backend/clustering/agglomerative.py

import pandas as pd
import numpy as np

from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
import os


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
# DENDROGRAM GENERATOR
# ======================================================

def generate_dendrogram(X, output_path):
    """
    Generate and save HAC dendrogram visualization.
    Uses ward linkage. Truncates to last 30 merged clusters to keep it readable.
    """
    plt.figure(figsize=(10, 6))
    plt.title("Hierarchical Clustering Dendrogram (Ward)")
    plt.xlabel("Cluster Size / Car Index")
    plt.ylabel("Distance (Ward)")
    
    Z = linkage(X, method='ward')
    dendrogram(
        Z,
        truncate_mode='lastp',
        p=30,  # show only the last 30 merged clusters
        show_leaf_counts=True,
        leaf_rotation=90.,
        leaf_font_size=10.,
        show_contracted=True,
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


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

        # Urban Agility (City Car): Irit, Lincah (Handling), Murah (Price index tinggi)
        scores["Urban Agility"] = (
            p["INDEX_EFFICIENCY"] +
            p["INDEX_HANDLING"] +
            p["INDEX_PRICE"] -
            p["INDEX_SPACE"]
        )

        # Family Comfort: Luas, Nyaman (proxy by Space), Aman (proxy by Handling/Power Balance)
        scores["Family Comfort"] = (
            p["INDEX_SPACE"] +
            p["INDEX_HANDLING"]
        )

        # Rugged Explorer: Ketangguhan (Offroad), Tenaga
        scores["Rugged Explorer"] = (
            p["INDEX_OFFROAD"] +
            p["INDEX_POWER"]
        )

        # High-End Performance: Tenaga Tinggi, Handling Tinggi, Prestisius (price index rendah = mahal)
        # Menghapus Luxury karena digabung ke sini
        scores["High-End Performance"] = (
            p["INDEX_POWER"] +
            p["INDEX_HANDLING"] -
            p.get("INDEX_PRICE", 0)
        )

        # Practical All-Rounder: Serba pas, lumayan irit (7), lumayan lega (7), harga oke (10)
        # Mencari cluster yang deviasinya paling kecil dari "Rata-rata ideal"
        scores["Practical All-Rounder"] = (
            p["INDEX_EFFICIENCY"] +
            p["INDEX_SPACE"] +
            p["INDEX_PRICE"]
        )

        score_table.append((cluster_id, scores))

    labels = ["Urban Agility", "Family Comfort", "Rugged Explorer", "High-End Performance", "Practical All-Rounder"]

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