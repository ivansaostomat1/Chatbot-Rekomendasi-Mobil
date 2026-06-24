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

RESULTS_DIR = r"results\baru"
OUTPUT_DIR = r"gambar bab 4"

os.makedirs(OUTPUT_DIR, exist_ok=True)

df_summary = pd.read_csv(os.path.join(RESULTS_DIR, "comparison_overview.csv"))
df_detail = pd.read_csv(os.path.join(RESULTS_DIR, "comparison_detail.csv"))
df_summary["gap(train-cv)"] = pd.to_numeric(df_summary["gap(train-cv)"], errors="coerce")

# --- Rename CP_baseline → Default (konsisten dengan configDefault.yml) ---
df_summary['config'] = df_summary['config'].replace('CP_baseline', 'Default')
rename_cols = {c: c.replace('CP_baseline', 'Default') for c in df_detail.columns if 'CP_baseline' in c}
df_detail = df_detail.rename(columns=rename_cols)

configs = ["Default", "TAv1", "TAv2", "TAv3", "TAv4", "TAv5", "TAv6"]
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

# ============================================================
# Gambar 4.10: Dashboard Scorecard "Satu Pandang"
# Heatmap komprehensif seluruh konfigurasi vs seluruh metrik kunci
# ============================================================

# Ambil data out_of_scope F1
intents_df = df_detail[df_detail["type"] == "intent"].copy()
oos_row = intents_df[intents_df["class"] == "out_of_scope"].iloc[0]

# Ambil data feature.negated F1 (sudah ada dari feat_neg)
scorecard_data = []
for conf in configs:
    row = df_summary[df_summary["config"] == conf].iloc[0]
    conf_csv = conf  # sudah di-rename
    scorecard_data.append({
        "Config": conf,
        "Intent\nF1": row["intent_f1_mean"],
        "Entity\nF1": row["entity_f1_mean"],
        "feature.\nnegated F1": float(feat_neg[f"{conf_csv}_f1"]),
        "out_of_\nscope F1": float(oos_row[f"{conf_csv}_f1"]),
        "Stabilitas\nIntent (std)": row["intent_f1_std"],
        "Stabilitas\nEntity (std)": row["entity_f1_std"],
        "Overfit\nGap": row["gap(train-cv)"],
    })

df_sc = pd.DataFrame(scorecard_data).set_index("Config")

# Tentukan apakah memenuhi kriteria
criteria = {
    "Intent\nF1":           lambda v: v >= 0.90,
    "Entity\nF1":           lambda v: v >= 0.90,
    "feature.\nnegated F1": lambda v: v >= 0.80,
    "out_of_\nscope F1":    lambda v: v >= 0.90,
    "Stabilitas\nIntent (std)": lambda v: v < 0.05,
    "Stabilitas\nEntity (std)": lambda v: v < 0.05,
    "Overfit\nGap":         lambda v: abs(v) < 0.05,
}

# Normalisasi untuk pewarnaan (semua dinormalisasi agar hijau=baik)
def normalize_for_color(df_sc):
    df_norm = pd.DataFrame(index=df_sc.index, columns=df_sc.columns, dtype=float)
    for col in df_sc.columns:
        vals = df_sc[col].values.astype(float)
        if "std" in col.lower() or "Gap" in col:
            # Lower is better → invert
            vmin, vmax = vals.min(), vals.max()
            if vmax != vmin:
                df_norm[col] = 1.0 - (vals - vmin) / (vmax - vmin)
            else:
                df_norm[col] = 0.5
        else:
            # Higher is better
            vmin, vmax = vals.min(), vals.max()
            if vmax != vmin:
                df_norm[col] = (vals - vmin) / (vmax - vmin)
            else:
                df_norm[col] = 0.5
    return df_norm

df_color = normalize_for_color(df_sc)

# Buat annotation text (nilai + ✅/❌)
annot_text = pd.DataFrame(index=df_sc.index, columns=df_sc.columns, dtype=str)
for col in df_sc.columns:
    for idx in df_sc.index:
        val = df_sc.loc[idx, col]
        passed = criteria[col](val)
        mark = "[OK]" if passed else "[X]"
        if "std" in col.lower():
            annot_text.loc[idx, col] = f"{val:.4f}\n{mark}"
        elif "Gap" in col:
            annot_text.loc[idx, col] = f"{val:+.4f}\n{mark}"
        else:
            annot_text.loc[idx, col] = f"{val:.4f}\n{mark}"

# Hitung total kriteria terpenuhi per config
pass_count = []
for conf in configs:
    count = sum(1 for col in df_sc.columns if criteria[col](df_sc.loc[conf, col]))
    pass_count.append(count)

# Plot
fig, ax = plt.subplots(figsize=(14, 6))
cmap = sns.color_palette("RdYlGn", as_cmap=True)

sns.heatmap(df_color.astype(float), annot=annot_text.values, fmt="", cmap=cmap,
            linewidths=1.5, linecolor='white', cbar=False, ax=ax,
            annot_kws={"fontsize": 9, "fontweight": "bold", "va": "center"})

# Tambah kolom "Lulus" di kanan
for i, (conf, count) in enumerate(zip(configs, pass_count)):
    color = "#2ca02c" if count >= 6 else ("#ff7f0e" if count >= 4 else "#d62728")
    ax.text(len(df_sc.columns) + 0.5, i + 0.5, f"{count}/7",
            ha="center", va="center", fontsize=12, fontweight="bold", color=color,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=color, linewidth=2))

ax.text(len(df_sc.columns) + 0.5, -0.3, "Kriteria\nTerpenuhi",
        ha="center", va="center", fontsize=9, fontweight="bold")

# Highlight baris terbaik
best_idx = pass_count.index(max(pass_count))
ax.add_patch(plt.Rectangle((0, best_idx), len(df_sc.columns), 1, fill=False,
             edgecolor='#2ca02c', linewidth=3, clip_on=False))

ax.set_title("Dashboard Scorecard: Perbandingan Seluruh Konfigurasi Pipeline NLU",
             fontsize=13, fontweight="bold", pad=15)
ax.set_ylabel("")
ax.set_xlabel("")
plt.xticks(rotation=0)
plt.yticks(rotation=0)

# Kriteria legend di bawah
criteria_text = ("Kriteria Kelulusan:  Intent F1 ≥ 0.90  |  Entity F1 ≥ 0.90  |  "
                 "feature.negated ≥ 0.80  |  out_of_scope ≥ 0.90  |  "
                 "Std < 0.05  |  |Gap| < 0.05")
fig.text(0.5, 0.01, criteria_text, ha="center", fontsize=8, fontstyle="italic", color="gray")
fig.text(0.98, 0.01, "[OK] = Lulus Kriteria  |  [X] = Tidak Lulus", ha="right", fontsize=8, color="gray")

plt.tight_layout(rect=[0, 0.04, 0.92, 1])
plt.savefig(os.path.join(OUTPUT_DIR, "Gambar 4.10.png"), dpi=300, bbox_inches="tight")
plt.close()

print("10 Gambar untuk revisi Bab 4 berhasil di-generate!")
