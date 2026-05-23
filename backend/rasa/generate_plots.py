import os
import pandas as pd
import numpy as np

# pyrefly: ignore [missing-import]
import matplotlib.pyplot as plt
import seaborn as sns
import json
from math import pi

plt.style.use("ggplot")
sns.set_palette("viridis")

RESULTS_DIR = r"results\comparison_20260512_145550"
OUTPUT_DIR = r"gambar bab 4"

os.makedirs(OUTPUT_DIR, exist_ok=True)

df_summary = pd.read_csv(os.path.join(RESULTS_DIR, "perbandingan.csv"))
df_detail = pd.read_csv(os.path.join(RESULTS_DIR, "detail perbandingan.csv"))
df_summary["gap(train-cv)"] = pd.to_numeric(df_summary["gap(train-cv)"], errors="coerce")

configs = ["CP_baseline", "TAv1", "TAv2", "TAv3", "TAv4", "TAv5", "TAv6"]
df_summary['config'] = pd.Categorical(df_summary['config'], categories=configs, ordered=True)
df_summary = df_summary.sort_values('config')

def add_hint(text):
    plt.figtext(0.98, 0.02, text, ha="right", fontsize=9, fontstyle="italic", color="gray")

# Gambar 4.1: Bar chart intent F1
plt.figure(figsize=(10, 6))
ax = sns.barplot(data=df_summary, x='config', y='intent_f1_mean', color='#1f77b4', edgecolor='black')
plt.errorbar(x=np.arange(len(configs)), y=df_summary['intent_f1_mean'], yerr=df_summary['intent_f1_std'], fmt='none', c='black', capsize=5)
plt.ylim(0.85, 0.92)
plt.title("Perbandingan Intent F1-Score Antar Konfigurasi", fontsize=12)
plt.xlabel("Konfigurasi")
plt.ylabel("Intent F1-Score")
for i, v in enumerate(df_summary['intent_f1_mean']):
    ax.text(i, v - 0.005, f"{v:.4f}", ha='center', color='white', fontweight='bold')
add_hint("* Lebih Tinggi Lebih Baik")
# Annotations inside plot
ax.annotate("TAv6: Rata-rata Tertinggi", xy=(6, 0.9044), xytext=(4, 0.915),
            arrowprops=dict(facecolor='black', arrowstyle='->'), fontsize=8, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
ax.annotate("Garis Hitam:\nStandar Deviasi\n(Makin panjang = Tidak stabil)", xy=(4, df_summary['intent_f1_mean'].iloc[4] + 0.005), xytext=(1.5, 0.91),
            arrowprops=dict(facecolor='black', arrowstyle='->'), fontsize=8, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "Gambar 4.1.png"), dpi=300)
plt.close()

# Gambar 4.2: Bar chart entity F1
plt.figure(figsize=(10, 6))
ax = sns.barplot(data=df_summary, x='config', y='entity_f1_mean', color='#ff7f0e', edgecolor='black')
plt.errorbar(x=np.arange(len(configs)), y=df_summary['entity_f1_mean'], yerr=df_summary['entity_f1_std'], fmt='none', c='black', capsize=5)
plt.ylim(0.88, 0.93)
plt.title("Perbandingan Entity F1-Score Antar Konfigurasi", fontsize=12)
plt.xlabel("Konfigurasi")
plt.ylabel("Entity F1-Score")
for i, v in enumerate(df_summary['entity_f1_mean']):
    ax.text(i, v - 0.005, f"{v:.4f}", ha='center', color='white', fontweight='bold')
add_hint("* Lebih Tinggi Lebih Baik")
ax.annotate("TAv6: Peningkatan Signifikan\n(Entity Terbaik)", xy=(6, 0.9206), xytext=(3.5, 0.925),
            arrowprops=dict(facecolor='black', arrowstyle='->'), fontsize=8, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "Gambar 4.2.png"), dpi=300)
plt.close()

# Gambar 4.3: Bar chart feature.negated
entities = df_detail[df_detail["type"] == "entity"].copy()
feat_neg = entities[entities["class"] == "feature.negated"].iloc[0]
feat_neg_f1 = [feat_neg[f"{conf}_f1"] for conf in configs]

plt.figure(figsize=(10, 6))
ax = sns.barplot(x=configs, y=feat_neg_f1, color='#d62728', edgecolor='black')
plt.ylim(0.5, 0.85)
plt.title("Perbandingan F1-Score Entitas feature.negated", fontsize=12)
plt.xlabel("Konfigurasi")
plt.ylabel("F1-Score (feature.negated)")
for i, v in enumerate(feat_neg_f1):
    ax.text(i, float(v) - 0.02, f"{float(v):.4f}", ha='center', color='white', fontweight='bold')
add_hint("* Lebih Tinggi Lebih Baik")
ax.annotate("TAv6: Satu-satunya model yang\nmemenuhi target minimal > 0.80", xy=(6, 0.8140), xytext=(2.5, 0.82),
            arrowprops=dict(facecolor='black', arrowstyle='->'), fontsize=8, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "Gambar 4.3.png"), dpi=300)
plt.close()

# Gambar 4.4: Line chart stabilitas (std)
df_melt_std = pd.melt(df_summary, id_vars=["config"], value_vars=["intent_f1_std", "entity_f1_std"], 
                      var_name="Metric", value_name="Std Dev")
df_melt_std["Metric"] = df_melt_std["Metric"].map({"intent_f1_std": "Intent Std Dev", "entity_f1_std": "Entity Std Dev"})

plt.figure(figsize=(10, 6))
ax = sns.lineplot(data=df_melt_std, x="config", y="Std Dev", hue="Metric", palette=['#1f77b4', '#d62728'], marker="o", linewidth=2.5, markersize=8)
plt.title("Stabilitas Model (Standar Deviasi Intent dan Entity)", fontsize=12)
plt.xlabel("Konfigurasi")
plt.ylabel("Standar Deviasi")
add_hint("* Lebih Rendah Lebih Baik (Lebih Stabil)")
val_tav5_intent = df_melt_std[(df_melt_std['config']=='TAv5') & (df_melt_std['Metric']=='Intent Std Dev')]['Std Dev'].values[0]
val_tav5_entity = df_melt_std[(df_melt_std['config']=='TAv5') & (df_melt_std['Metric']=='Entity Std Dev')]['Std Dev'].values[0]
mid_tav5 = (val_tav5_intent + val_tav5_entity) / 2
ax.annotate("TAv5 Paling Stabil:\nKedua garis (Intent & Entity)\nrendah dan saling berdekatan", 
            xy=(5, mid_tav5), xytext=(0.5, 0.013),
            arrowprops=dict(facecolor='black', arrowstyle='->'), fontsize=9, bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "Gambar 4.4.png"), dpi=300)
plt.close()

# Gambar 4.5: Line plot overfitting gap
plt.figure(figsize=(10, 6))
# Menggunakan lineplot sesuai narasi teks Bab 4
ax = sns.lineplot(data=df_summary, x='config', y='gap(train-cv)', marker="o", color='purple', linewidth=2.5, markersize=8)
plt.axhline(0, color='black', linewidth=1)
plt.axhline(0.05, color='gray', linestyle='--', linewidth=1, label="Batas Generalisasi Baik (0.05)")
plt.legend()
plt.title("Overfitting Gap (Train F1 - CV F1)", fontsize=12)
plt.xlabel("Konfigurasi")
plt.ylabel("Gap F1-Score")
add_hint("* Mendekati 0 / Negatif Lebih Baik")
gap_tav5 = df_summary[df_summary['config']=='TAv5']['gap(train-cv)'].values[0]
ax.annotate("TAv5: Generalisasi Terbaik\n(Batang Hijau = Tidak Overfit)", xy=(5, gap_tav5), xytext=(1, 0.08),
            arrowprops=dict(facecolor='black', arrowstyle='->'), fontsize=9, bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "Gambar 4.5.png"), dpi=300)
plt.close()

# Gambar 4.6: Scatter plot Gap vs Entity F1
plt.figure(figsize=(8, 6))
ax = sns.scatterplot(data=df_summary, x='gap(train-cv)', y='entity_f1_mean', s=150, color='purple', edgecolor='black')
for i, row in df_summary.iterrows():
    ax.text(row['gap(train-cv)'], row['entity_f1_mean'] + 0.001, row['config'], horizontalalignment='center', fontsize=10)
plt.axvline(0.05, color='gray', linestyle='--', linewidth=1)
plt.title("Trade-off Generalisasi (Gap) vs Performa (Entity F1)", fontsize=12)
plt.xlabel("Overfitting Gap (Train - CV)")
plt.ylabel("Entity F1-Score Mean")
add_hint("* Kiri Atas (Gap Rendah, F1 Tinggi) Lebih Baik")
tav6_row = df_summary[df_summary['config']=='TAv6'].iloc[0]
tav5_row = df_summary[df_summary['config']=='TAv5'].iloc[0]
ax.annotate("TAv6:\nUnggul\nPerforma", xy=(tav6_row['gap(train-cv)'], tav6_row['entity_f1_mean']), 
            xytext=(0.08, 0.89),
            arrowprops=dict(facecolor='black', arrowstyle='->'), fontsize=9, bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
ax.annotate("TAv5:\nUnggul\nGeneralisasi", xy=(tav5_row['gap(train-cv)'], tav5_row['entity_f1_mean']), 
            xytext=(-0.02, 0.92),
            arrowprops=dict(facecolor='black', arrowstyle='->'), fontsize=9, bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "Gambar 4.6.png"), dpi=300)
plt.close()

# Gambar 4.7: Radar chart TAv4, TAv5, TAv6
body_neg = entities[entities["class"] == "body_type.negated"].iloc[0]
target_configs = ["TAv4", "TAv5", "TAv6"]

def minmax(val, min_val, max_val):
    return (val - min_val) / (max_val - min_val) if max_val != min_val else 0.5

raw_data = []
for conf in target_configs:
    row = df_summary[df_summary["config"] == conf].iloc[0]
    raw_data.append({
        "conf": conf,
        "Intent F1": row["intent_f1_mean"],
        "Entity F1": row["entity_f1_mean"],
        "feature.negated F1": float(feat_neg[f"{conf}_f1"]),
        "body_type.negated F1": float(body_neg[f"{conf}_f1"]),
        "Stabilitas Intent": 1.0 / row["intent_f1_std"],
        "Stabilitas Entity": 1.0 / row["entity_f1_std"],
        "Generalisasi (Gap)": 1.0 / (abs(row["gap(train-cv)"]) + 0.001)
    })
df_raw = pd.DataFrame(raw_data)

categories = ["Intent F1", "Entity F1", "feature.negated F1", "body_type.negated F1", 
              "Stabilitas Intent", "Stabilitas Entity", "Generalisasi (Gap)"]
N = len(categories)

all_raw = []
for conf in configs:
    row = df_summary[df_summary["config"] == conf].iloc[0]
    all_raw.append({
        "Intent F1": row["intent_f1_mean"],
        "Entity F1": row["entity_f1_mean"],
        "feature.negated F1": float(feat_neg[f"{conf}_f1"]),
        "body_type.negated F1": float(body_neg[f"{conf}_f1"]),
        "Stabilitas Intent": 1.0 / row["intent_f1_std"],
        "Stabilitas Entity": 1.0 / row["entity_f1_std"],
        "Generalisasi (Gap)": 1.0 / (abs(row["gap(train-cv)"]) + 0.001)
    })
df_all = pd.DataFrame(all_raw)

df_norm = pd.DataFrame()
for cat in categories:
    min_val = df_all[cat].min()
    max_val = df_all[cat].max()
    df_norm[cat] = df_raw[cat].apply(lambda x: minmax(x, min_val, max_val))

angles = [n / float(N) * 2 * pi for n in range(N)]
angles += angles[:1]

plt.figure(figsize=(8, 8))
ax = plt.subplot(111, polar=True)
ax.set_theta_offset(pi / 2)
ax.set_theta_direction(-1)
plt.xticks(angles[:-1], categories, size=9)
ax.set_rlabel_position(0)
plt.yticks([0.2, 0.4, 0.6, 0.8, 1.0], ["", "", "", "", ""], color="grey", size=7)
plt.ylim(0, 1.05)

colors_radar = ["#1f77b4", "#2ca02c", "#d62728"]
for i, conf in enumerate(target_configs):
    values = df_norm.iloc[i].values.flatten().tolist()
    values += values[:1]
    ax.plot(angles, values, linewidth=2, linestyle="solid", label=conf, color=colors_radar[i])
    ax.fill(angles, values, colors_radar[i], alpha=0.1)

plt.legend(loc="upper right", bbox_to_anchor=(0.1, 0.1))
plt.title("Radar Chart Komparatif 3 Konfigurasi Terbaik (Normalized)", fontsize=12, pad=20)
add_hint("* Area Lebih Luas / Mendekati Tepi Lebih Baik")
ax.text(0.5, 1.15, "TAv6 (Merah): Mendominasi Performa\nTAv5 (Hijau): Mendominasi Stabilitas", 
        transform=ax.transAxes, ha='center', fontsize=9, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "Gambar 4.7.png"), dpi=300)
plt.close()

# Helper for Confusion Matrix
def plot_cm(conf_name, title, filename):
    # Cek folder cv_run1 atau cv_run_1
    folder_name = "cv_run1" if os.path.exists(os.path.join(RESULTS_DIR, conf_name, "cv_run1")) else "cv_run_1"
    
    cm_path = os.path.join(RESULTS_DIR, conf_name, folder_name, f"{conf_name}_{folder_name}_intent_report.json")
    if not os.path.exists(cm_path):
        cm_path = os.path.join(RESULTS_DIR, conf_name, folder_name, "intent_report.json")
    
    if os.path.exists(cm_path):
        with open(cm_path, "r") as f:
            data = json.load(f)
        classes = [k for k in data.keys() if k not in ["accuracy", "macro avg", "weighted avg", "micro avg"]]
        cm = pd.DataFrame(0.0, index=classes, columns=classes)
        for cls in classes:
            support = data[cls]["support"]
            recall = data[cls]["recall"]
            correct = int(round(support * recall))
            cm.loc[cls, cls] = correct
            confused = data[cls].get("confused_with", {})
            for c_cls, count in confused.items():
                if c_cls in classes:
                    cm.loc[cls, c_cls] = count
                
        cm_norm = cm.div(cm.sum(axis=1), axis=0)
        plt.figure(figsize=(8, 6))
        ax = sns.heatmap(cm_norm, annot=cm.astype(int), fmt="d", cmap="Blues", cbar=False)
        plt.title(title, fontsize=12)
        plt.ylabel("True Label")
        plt.xlabel("Predicted Label")
        plt.xticks(rotation=45, ha="right")
        add_hint("* Angka Terpusat di Diagonal Utama Lebih Baik")
        ax.text(0.98, 0.98, "Diagonal Utama = Prediksi Benar", transform=ax.transAxes, 
                ha='right', va='top', fontsize=9, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300)
        plt.close()

# Gambar 4.8: CM TAv5
plot_cm("TAv5", "Heatmap Confusion Matrix Intent TAv5", "Gambar 4.8.png")

# Gambar 4.9: CM TAv6
plot_cm("TAv6", "Heatmap Confusion Matrix Intent TAv6", "Gambar 4.9.png")

print("9 Gambar untuk revisi Bab 4 berhasil di-generate!")
