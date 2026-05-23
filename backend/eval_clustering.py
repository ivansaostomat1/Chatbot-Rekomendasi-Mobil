# eval_clustering.py
# ================================================================
# Evaluasi Pemilihan Nilai K untuk K-Means Clustering
# Menggunakan Elbow Method + Silhouette Score + Calinski-Harabasz
# ================================================================
# Jalankan: python eval_clustering.py
# Output : Grafik evaluasi + tabel numerik + distribusi cluster
# ================================================================

import os
import sys
import warnings
warnings.filterwarnings("ignore")

# Path injection
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score

from app.data_loader import load_all_datasets
from app.feature_engineering.pipeline import generate_feature_dataset

# ================================================================
# KONFIGURASI
# ================================================================
K_RANGE = range(2, 16)       # Evaluasi k=2 sampai k=15
CHOSEN_K = 8                 # Nilai k yang digunakan di sistem
RANDOM_STATE = 42
N_INIT = 10
OUTPUT_DIR = os.path.join(current_dir, "results", "clustering")

FEATURES = [
    'HORSE POWER (HP)',
    'TORQUE (Nm)',
    'GROUND CLEARANCE',
    'WHEELBASE',
    'LONG',
    'WIDTH',
    'HEIGHT'
]

# ================================================================
# 1. LOAD & PREPROCESS DATA (sama persis dengan clustering.py)
# ================================================================
print("=" * 65)
print("  EVALUASI K-MEANS CLUSTERING — PEMILIHAN NILAI K")
print("=" * 65)

print("\n[1/5] Loading dataset...")
import io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
mobil, wholesales, retail = load_all_datasets()
df = generate_feature_dataset(mobil, wholesales, retail)

# Fill missing values with median (sama dengan clustering.py)
for feature in FEATURES:
    if feature in df.columns:
        df[feature] = df[feature].fillna(df[feature].median())

X = df[FEATURES].values
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print(f"    Dataset  : {len(df)} varian kendaraan")
print(f"    Model    : {df.groupby(['BRAND', 'MODEL']).ngroups} model unik")
print(f"    Fitur    : {len(FEATURES)} fitur fisik")
for f in FEATURES:
    print(f"               • {f}")

# ================================================================
# 2. EVALUASI METRIK UNTUK SETIAP K
# ================================================================
print(f"\n[2/5] Evaluasi K-Means untuk k={K_RANGE.start} sampai k={K_RANGE.stop - 1}...")

results = []
for k in K_RANGE:
    kmeans = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=N_INIT)
    labels = kmeans.fit_predict(X_scaled)

    inertia = kmeans.inertia_
    sil = silhouette_score(X_scaled, labels)
    cal = calinski_harabasz_score(X_scaled, labels)
    dbi = davies_bouldin_score(X_scaled, labels)

    results.append({
        "k": k,
        "inertia": inertia,
        "silhouette": sil,
        "calinski_harabasz": cal,
        "davies_bouldin": dbi,
    })

    marker = " << DIPILIH" if k == CHOSEN_K else ""
    print(f"    k={k:2d}  |  Inertia={inertia:8.1f}  |  Silhouette={sil:.4f}  |  CH={cal:8.1f}  |  DBI={dbi:.4f}{marker}")

results_df = pd.DataFrame(results)

# ================================================================
# 3. ANALISIS CLUSTER TERPILIH (k=8)
# ================================================================
print(f"\n[3/5] Analisis distribusi cluster untuk k={CHOSEN_K}...")

kmeans_chosen = KMeans(n_clusters=CHOSEN_K, random_state=RANDOM_STATE, n_init=N_INIT)
df["CLUSTER"] = kmeans_chosen.fit_predict(X_scaled)

# Distribusi per cluster
print(f"\n    {'Cluster':>8} | {'Varian':>7} | {'Model Unik':>11} | {'Rata-rata HP':>13} | {'Rata-rata GC':>13} | Contoh Mobil")
print("    " + "-" * 100)

for c in sorted(df["CLUSTER"].unique()):
    cluster_df = c_df = df[df["CLUSTER"] == c]
    n_varian = len(cluster_df)
    n_model = cluster_df.groupby(["BRAND", "MODEL"]).ngroups
    avg_hp = cluster_df["HORSE POWER (HP)"].mean()
    avg_gc = cluster_df["GROUND CLEARANCE"].mean()

    # Ambil 3 contoh mobil unik
    examples = cluster_df.groupby(["BRAND", "MODEL"]).first().reset_index()
    example_names = [f"{r['BRAND'].title()} {r['MODEL'].title()}" for _, r in examples.head(3).iterrows()]
    example_str = ", ".join(example_names)

    print(f"    {c:>8} | {n_varian:>7} | {n_model:>11} | {avg_hp:>13.1f} | {avg_gc:>13.1f} | {example_str}")

# ================================================================
# 4. BUAT GRAFIK EVALUASI
# ================================================================
print(f"\n[4/5] Membuat grafik evaluasi...")
os.makedirs(OUTPUT_DIR, exist_ok=True)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Evaluasi Pemilihan Nilai K — K-Means Clustering", fontsize=15, fontweight="bold", y=0.98)

k_values = results_df["k"].values

# --- Plot 1: Elbow Method (Inertia / SSE) ---
ax1 = axes[0, 0]
ax1.plot(k_values, results_df["inertia"], "o-", color="#2563EB", linewidth=2, markersize=6)
ax1.axvline(x=CHOSEN_K, color="#DC2626", linestyle="--", alpha=0.7, label=f"k={CHOSEN_K} (dipilih)")
ax1.scatter([CHOSEN_K], [results_df[results_df["k"] == CHOSEN_K]["inertia"].values[0]],
            color="#DC2626", s=120, zorder=5, edgecolors="white", linewidth=2)
ax1.set_title("Elbow Method (Sum of Squared Errors)", fontweight="bold")
ax1.set_xlabel("Jumlah Cluster (k)")
ax1.set_ylabel("Inertia (SSE)")
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.xaxis.set_major_locator(MaxNLocator(integer=True))

# --- Plot 2: Silhouette Score ---
ax2 = axes[0, 1]
colors = ["#DC2626" if k == CHOSEN_K else "#2563EB" for k in k_values]
bars = ax2.bar(k_values, results_df["silhouette"], color=colors, alpha=0.8, edgecolor="white")
ax2.set_title("Silhouette Score (Semakin Tinggi = Semakin Baik)", fontweight="bold")
ax2.set_xlabel("Jumlah Cluster (k)")
ax2.set_ylabel("Silhouette Score")
ax2.grid(True, alpha=0.3, axis="y")
ax2.xaxis.set_major_locator(MaxNLocator(integer=True))
# Annotate chosen k
chosen_sil = results_df[results_df["k"] == CHOSEN_K]["silhouette"].values[0]
ax2.annotate(f"k={CHOSEN_K}\n{chosen_sil:.4f}",
             xy=(CHOSEN_K, chosen_sil), xytext=(CHOSEN_K + 1.5, chosen_sil + 0.02),
             arrowprops=dict(arrowstyle="->", color="#DC2626"),
             fontsize=9, fontweight="bold", color="#DC2626")

# --- Plot 3: Calinski-Harabasz Index ---
ax3 = axes[1, 0]
ax3.plot(k_values, results_df["calinski_harabasz"], "s-", color="#059669", linewidth=2, markersize=6)
ax3.axvline(x=CHOSEN_K, color="#DC2626", linestyle="--", alpha=0.7, label=f"k={CHOSEN_K} (dipilih)")
ax3.scatter([CHOSEN_K], [results_df[results_df["k"] == CHOSEN_K]["calinski_harabasz"].values[0]],
            color="#DC2626", s=120, zorder=5, edgecolors="white", linewidth=2)
ax3.set_title("Calinski-Harabasz Index (Semakin Tinggi = Semakin Baik)", fontweight="bold")
ax3.set_xlabel("Jumlah Cluster (k)")
ax3.set_ylabel("CH Index")
ax3.legend()
ax3.grid(True, alpha=0.3)
ax3.xaxis.set_major_locator(MaxNLocator(integer=True))

# --- Plot 4: Davies-Bouldin Index ---
ax4 = axes[1, 1]
ax4.plot(k_values, results_df["davies_bouldin"], "D-", color="#7C3AED", linewidth=2, markersize=6)
ax4.axvline(x=CHOSEN_K, color="#DC2626", linestyle="--", alpha=0.7, label=f"k={CHOSEN_K} (dipilih)")
ax4.scatter([CHOSEN_K], [results_df[results_df["k"] == CHOSEN_K]["davies_bouldin"].values[0]],
            color="#DC2626", s=120, zorder=5, edgecolors="white", linewidth=2)
ax4.set_title("Davies-Bouldin Index (Semakin Rendah = Semakin Baik)", fontweight="bold")
ax4.set_xlabel("Jumlah Cluster (k)")
ax4.set_ylabel("DBI")
ax4.legend()
ax4.grid(True, alpha=0.3)
ax4.xaxis.set_major_locator(MaxNLocator(integer=True))

plt.tight_layout(rect=[0, 0, 1, 0.95])
plot_path = os.path.join(OUTPUT_DIR, "kmeans_evaluation.png")
plt.savefig(plot_path, dpi=200, bbox_inches="tight")
plt.close()
print(f"    Grafik disimpan: {plot_path}")

# ================================================================
# 5. BUAT GRAFIK DISTRIBUSI CLUSTER
# ================================================================
fig2, axes2 = plt.subplots(1, 2, figsize=(14, 5))
fig2.suptitle(f"Distribusi Cluster (k={CHOSEN_K})", fontsize=14, fontweight="bold")

# Bar chart distribusi
cluster_counts = df["CLUSTER"].value_counts().sort_index()
colors_bar = plt.cm.Set2(np.linspace(0, 1, CHOSEN_K))
axes2[0].bar(cluster_counts.index, cluster_counts.values, color=colors_bar, edgecolor="white", linewidth=1.5)
axes2[0].set_title("Jumlah Varian per Cluster", fontweight="bold")
axes2[0].set_xlabel("Cluster")
axes2[0].set_ylabel("Jumlah Varian")
axes2[0].xaxis.set_major_locator(MaxNLocator(integer=True))
for i, (idx, val) in enumerate(cluster_counts.items()):
    axes2[0].text(idx, val + 1, str(val), ha="center", fontweight="bold", fontsize=9)

# Box plot HP per cluster (contoh separasi fitur)
cluster_groups = [df[df["CLUSTER"] == c]["HORSE POWER (HP)"].values for c in sorted(df["CLUSTER"].unique())]
bp = axes2[1].boxplot(cluster_groups, labels=[str(c) for c in sorted(df["CLUSTER"].unique())],
                      patch_artist=True, medianprops=dict(color="black", linewidth=2))
for patch, color in zip(bp["boxes"], colors_bar):
    patch.set_facecolor(color)
    patch.set_alpha(0.8)
axes2[1].set_title("Distribusi Horse Power per Cluster", fontweight="bold")
axes2[1].set_xlabel("Cluster")
axes2[1].set_ylabel("Horse Power (HP)")

plt.tight_layout()
dist_path = os.path.join(OUTPUT_DIR, "cluster_distribution.png")
plt.savefig(dist_path, dpi=200, bbox_inches="tight")
plt.close()
print(f"    Distribusi disimpan: {dist_path}")

# ================================================================
# 6. SIMPAN TABEL HASIL KE CSV
# ================================================================
csv_path = os.path.join(OUTPUT_DIR, "kmeans_evaluation_results.csv")
results_df.to_csv(csv_path, index=False)
print(f"    Tabel CSV disimpan: {csv_path}")

# ================================================================
# RINGKASAN
# ================================================================
chosen_row = results_df[results_df["k"] == CHOSEN_K].iloc[0]
best_sil_k = results_df.loc[results_df["silhouette"].idxmax(), "k"]
best_ch_k = results_df.loc[results_df["calinski_harabasz"].idxmax(), "k"]
best_dbi_k = results_df.loc[results_df["davies_bouldin"].idxmin(), "k"]

print(f"\n[5/5] RINGKASAN EVALUASI")
print("=" * 65)
print(f"  Nilai k yang dipilih       : {CHOSEN_K}")
print(f"  Inertia (SSE)              : {chosen_row['inertia']:.1f}")
print(f"  Silhouette Score           : {chosen_row['silhouette']:.4f}")
print(f"  Calinski-Harabasz Index    : {chosen_row['calinski_harabasz']:.1f}")
print(f"  Davies-Bouldin Index       : {chosen_row['davies_bouldin']:.4f}")
print(f"")
print(f"  K terbaik per metrik:")
print(f"    • Silhouette Score       : k={int(best_sil_k)} (max={results_df['silhouette'].max():.4f})")
print(f"    • Calinski-Harabasz      : k={int(best_ch_k)} (max={results_df['calinski_harabasz'].max():.1f})")
print(f"    • Davies-Bouldin         : k={int(best_dbi_k)} (min={results_df['davies_bouldin'].min():.4f})")
print(f"")

# Interpretasi otomatis
print(f"  INTERPRETASI:")
if CHOSEN_K == best_sil_k:
    print(f"    [OK] k={CHOSEN_K} adalah OPTIMAL menurut Silhouette Score")
elif abs(chosen_row['silhouette'] - results_df['silhouette'].max()) < 0.02:
    print(f"    [~] k={CHOSEN_K} mendekati optimal Silhouette (selisih < 0.02 dari k={int(best_sil_k)})")
else:
    print(f"    [!] k={int(best_sil_k)} lebih optimal menurut Silhouette, tapi k={CHOSEN_K} dipilih")
    print(f"       karena trade-off antara granularitas cluster dan relevansi rekomendasi")

avg_per_cluster = len(df) / CHOSEN_K
print(f"    [i] Rata-rata {avg_per_cluster:.0f} varian per cluster ({len(df)} total / {CHOSEN_K} cluster)")
print(f"       Cukup besar untuk rekomendasi beragam, cukup kecil untuk relevansi tinggi")
print("=" * 65)
print(f"\n  Output tersimpan di: {OUTPUT_DIR}/")
print("  Selesai!\n")
