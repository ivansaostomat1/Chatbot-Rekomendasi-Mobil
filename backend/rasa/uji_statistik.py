"""
uji_statistik.py
================
Script untuk melakukan uji statistik pada hasil eksperimen NLU pipeline.
Mengekstrak F1-Score per-run dari setiap konfigurasi, lalu menjalankan:
  1. Shapiro-Wilk (normalitas)
  2. Paired T-Test / Wilcoxon Signed-Rank Test (signifikansi)
  3. Cohen's d / Rank-biserial correlation (effect size)

Hasil disimpan ke file CSV dan ditampilkan di terminal.

Penggunaan:
  python uji_statistik.py
"""

import os
import json
import numpy as np
from scipy import stats
from itertools import combinations

# ==============================================================================
# KONFIGURASI
# ==============================================================================
RESULTS_DIR = os.path.join("results", "baru")

CONFIGS = {
    "CP": "Default",
    "TAv1": "TAv1",
    "TAv2": "TAv2",
    "TAv3": "TAv3",
    "TAv4": "TAv4",
    "TAv5": "TAv5",
    "TAv6": "TAv6",
}

N_RUNS = 3
ALPHA = 0.05

# Pasangan uji kunci berdasarkan hipotesis
HYPOTHESIS_PAIRS = {
    "H1: IndoBERT vs Default": [
        ("CP", "TAv2"),
        ("TAv1", "TAv2"),
    ],
    "H2: Rule-based+Linguistik vs IndoBERT saja": [
        ("TAv2", "TAv4"),
        ("TAv4", "TAv5"),
    ],
    "H3: Hybrid vs lainnya": [
        ("TAv2", "TAv6"),
        ("TAv5", "TAv6"),
        ("CP", "TAv6"),
    ],
}


# ==============================================================================
# FUNGSI EKSTRAKSI DATA
# ==============================================================================
def extract_f1_per_run(config_label, config_folder, metric_type="intent"):
    """
    Ekstrak F1-Score macro avg dari setiap cv_run.
    
    Args:
        config_label: Label konfigurasi (e.g., "CP")
        config_folder: Nama folder di results (e.g., "Default")
        metric_type: "intent" atau "entity"
    
    Returns:
        List of F1-scores, satu per run
    """
    f1_values = []
    
    for run_idx in range(1, N_RUNS + 1):
        run_dir = os.path.join(RESULTS_DIR, config_folder, f"cv_run{run_idx}")
        
        if metric_type == "intent":
            # File: {folder}_cv_run{n}_intent_report.json
            filename = f"{config_folder}_cv_run{run_idx}_intent_report.json"
        else:
            # File: {folder}_cv_run{n}_DIETClassifier_report.json
            filename = f"{config_folder}_cv_run{run_idx}_DIETClassifier_report.json"
        
        filepath = os.path.join(run_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"  [WARNING] File tidak ditemukan: {filepath}")
            continue
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Ambil macro avg f1-score
        if "macro avg" in data:
            f1 = data["macro avg"]["f1-score"]
            f1_values.append(f1)
        else:
            print(f"  [WARNING] 'macro avg' tidak ada di {filepath}")
    
    return f1_values


def extract_per_class_f1(config_folder, class_name, metric_type="entity"):
    """
    Ekstrak F1-Score per kelas dari setiap cv_run.
    """
    f1_values = []
    
    for run_idx in range(1, N_RUNS + 1):
        run_dir = os.path.join(RESULTS_DIR, config_folder, f"cv_run{run_idx}")
        
        if metric_type == "intent":
            filename = f"{config_folder}_cv_run{run_idx}_intent_report.json"
        else:
            filename = f"{config_folder}_cv_run{run_idx}_DIETClassifier_report.json"
        
        filepath = os.path.join(run_dir, filename)
        
        if not os.path.exists(filepath):
            continue
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if class_name in data:
            f1_values.append(data[class_name]["f1-score"])
    
    return f1_values


# ==============================================================================
# FUNGSI UJI STATISTIK
# ==============================================================================
def shapiro_wilk_test(values, label):
    """Uji normalitas Shapiro-Wilk."""
    if len(values) < 3:
        return None, "Data terlalu sedikit"
    
    stat, p_value = stats.shapiro(values)
    is_normal = p_value > ALPHA
    return {
        "label": label,
        "n": len(values),
        "statistic": round(stat, 4),
        "p_value": round(p_value, 4),
        "is_normal": is_normal,
        "interpretation": "Normal" if is_normal else "Tidak Normal"
    }


def significance_test(values_a, values_b, label_a, label_b, both_normal):
    """
    Uji signifikansi: Paired T-Test (jika normal) atau Wilcoxon (jika tidak).
    """
    n = min(len(values_a), len(values_b))
    if n < 2:
        return None
    
    a = np.array(values_a[:n])
    b = np.array(values_b[:n])
    
    if both_normal:
        stat, p_value = stats.ttest_rel(a, b)
        test_name = "Paired T-Test"
    else:
        # Wilcoxon requires non-zero differences
        diff = a - b
        if np.all(diff == 0):
            return {
                "pair": f"{label_a} vs {label_b}",
                "test": "N/A",
                "statistic": 0,
                "p_value": 1.0,
                "significant": False,
                "interpretation": "Tidak ada perbedaan",
                "effect_size": 0,
                "effect_label": "N/A"
            }
        stat, p_value = stats.wilcoxon(a, b)
        test_name = "Wilcoxon"
    
    significant = p_value < ALPHA
    
    # Effect size
    if both_normal:
        # Cohen's d
        diff = a - b
        d = np.mean(diff) / np.std(diff, ddof=1) if np.std(diff, ddof=1) > 0 else 0
        effect = abs(d)
        if effect < 0.2:
            effect_label = "Kecil"
        elif effect < 0.8:
            effect_label = "Sedang"
        else:
            effect_label = "Besar"
        effect_name = f"Cohen's d = {round(d, 4)}"
    else:
        # Rank-biserial correlation
        r = 1 - (2 * stat) / (n * (n + 1) / 2)
        effect = abs(r)
        if effect < 0.3:
            effect_label = "Kecil"
        elif effect < 0.5:
            effect_label = "Sedang"
        else:
            effect_label = "Besar"
        effect_name = f"r = {round(r, 4)}"
    
    return {
        "pair": f"{label_a} vs {label_b}",
        "test": test_name,
        "statistic": round(stat, 4),
        "p_value": round(p_value, 4),
        "significant": significant,
        "interpretation": "Signifikan" if significant else "Tidak Signifikan",
        "effect_size": effect_name,
        "effect_label": effect_label,
        "mean_a": round(np.mean(a), 4),
        "mean_b": round(np.mean(b), 4),
        "diff": round(np.mean(b) - np.mean(a), 4),
    }


# ==============================================================================
# MAIN
# ==============================================================================
def main():
    print("=" * 80)
    print("UJI STATISTIK HASIL EKSPERIMEN NLU PIPELINE")
    print("=" * 80)
    
    # -----------------------------------------------------------
    # 1. EKSTRAKSI DATA
    # -----------------------------------------------------------
    print("\n[1/4] Mengekstrak F1-Score per-run dari setiap konfigurasi...\n")
    
    intent_f1 = {}
    entity_f1 = {}
    feature_neg_f1 = {}
    
    for label, folder in CONFIGS.items():
        intent_vals = extract_f1_per_run(label, folder, "intent")
        entity_vals = extract_f1_per_run(label, folder, "entity")
        feat_neg_vals = extract_per_class_f1(folder, "feature.negated", "entity")
        
        intent_f1[label] = intent_vals
        entity_f1[label] = entity_vals
        feature_neg_f1[label] = feat_neg_vals
        
        print(f"  {label:6s}: Intent F1 = {[round(v,4) for v in intent_vals]}, "
              f"Entity F1 = {[round(v,4) for v in entity_vals]}, "
              f"feature.negated F1 = {[round(v,4) for v in feat_neg_vals]}")
    
    # -----------------------------------------------------------
    # 2. UJI NORMALITAS (SHAPIRO-WILK)
    # -----------------------------------------------------------
    print("\n" + "=" * 80)
    print("[2/4] UJI NORMALITAS (Shapiro-Wilk, alpha = 0.05)")
    print("=" * 80)
    
    normality_results = {}
    
    for metric_name, data_dict in [("Intent F1", intent_f1), ("Entity F1", entity_f1)]:
        print(f"\n--- {metric_name} ---")
        print(f"{'Config':<8} {'n':>3} {'W-stat':>8} {'p-value':>8} {'Hasil':>15}")
        print("-" * 50)
        
        for label in CONFIGS:
            result = shapiro_wilk_test(data_dict[label], f"{label}_{metric_name}")
            if result:
                normality_results[f"{label}_{metric_name}"] = result
                print(f"{label:<8} {result['n']:>3} {result['statistic']:>8.4f} "
                      f"{result['p_value']:>8.4f} {result['interpretation']:>15}")
    
    # -----------------------------------------------------------
    # 3. UJI SIGNIFIKANSI + EFFECT SIZE
    # -----------------------------------------------------------
    print("\n" + "=" * 80)
    print("[3/4] UJI SIGNIFIKANSI & EFFECT SIZE (alpha = 0.05)")
    print("=" * 80)
    
    all_sig_results = []
    
    for hypothesis, pairs in HYPOTHESIS_PAIRS.items():
        print(f"\n{'='*60}")
        print(f"  {hypothesis}")
        print(f"{'='*60}")
        
        for metric_name, data_dict in [("Intent F1", intent_f1), ("Entity F1", entity_f1)]:
            print(f"\n  --- {metric_name} ---")
            
            for label_a, label_b in pairs:
                # Cek normalitas kedua distribusi
                key_a = f"{label_a}_{metric_name}"
                key_b = f"{label_b}_{metric_name}"
                
                normal_a = normality_results.get(key_a, {}).get("is_normal", False)
                normal_b = normality_results.get(key_b, {}).get("is_normal", False)
                both_normal = normal_a and normal_b
                
                result = significance_test(
                    data_dict[label_a], data_dict[label_b],
                    label_a, label_b, both_normal
                )
                
                if result:
                    result["metric"] = metric_name
                    result["hypothesis"] = hypothesis
                    all_sig_results.append(result)
                    
                    sig_marker = "***" if result["significant"] else "   "
                    print(f"    {result['pair']:20s} | {result['test']:15s} | "
                          f"p={result['p_value']:.4f} {sig_marker} | "
                          f"{result['effect_size']:>20s} ({result['effect_label']}) | "
                          f"Diff={result['diff']:+.4f}")
    
    # -----------------------------------------------------------
    # 4. ANALISIS FEATURE.NEGATED (fokus khusus)
    # -----------------------------------------------------------
    print("\n" + "=" * 80)
    print("[4/4] ANALISIS KHUSUS: feature.negated F1")
    print("=" * 80)
    
    key_pairs_negasi = [
        ("CP", "TAv6"),
        ("TAv2", "TAv6"),
        ("TAv5", "TAv6"),
    ]
    
    for label_a, label_b in key_pairs_negasi:
        vals_a = feature_neg_f1[label_a]
        vals_b = feature_neg_f1[label_b]
        
        if len(vals_a) >= 2 and len(vals_b) >= 2:
            # Gunakan Wilcoxon karena n kecil (3)
            result = significance_test(vals_a, vals_b, label_a, label_b, False)
            if result:
                sig_marker = "***" if result["significant"] else "   "
                print(f"  {result['pair']:20s} | {result['test']:15s} | "
                      f"p={result['p_value']:.4f} {sig_marker} | "
                      f"mean: {result['mean_a']:.4f} -> {result['mean_b']:.4f} "
                      f"(Diff={result['diff']:+.4f})")
    
    # -----------------------------------------------------------
    # RINGKASAN
    # -----------------------------------------------------------
    print("\n" + "=" * 80)
    print("RINGKASAN KONFIRMASI HIPOTESIS")
    print("=" * 80)
    
    print("""
Catatan: Dengan hanya 3 nilai per konfigurasi (3 runs), kekuatan uji statistik 
(statistical power) terbatas. Hasil ini bersifat indikatif dan harus diinterpretasikan 
bersama dengan analisis deskriptif yang telah dilakukan di BAB 4.

Kriteria konfirmasi:
  - p < 0.05: Perbedaan signifikan secara statistik
  - p >= 0.05: H0 tidak dapat ditolak (perbedaan tidak signifikan)
    """)
    
    # Simpan ke CSV
    output_csv = os.path.join(RESULTS_DIR, "uji_statistik_hasil.csv")
    try:
        import csv
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                "hypothesis", "metric", "pair", "test", "statistic", 
                "p_value", "significant", "interpretation",
                "effect_size", "effect_label", "mean_a", "mean_b", "diff"
            ])
            writer.writeheader()
            for r in all_sig_results:
                writer.writerow(r)
        print(f"\nHasil disimpan ke: {output_csv}")
    except Exception as e:
        print(f"\n[ERROR] Gagal menyimpan CSV: {e}")
    
    print("\nSelesai.")


if __name__ == "__main__":
    main()
