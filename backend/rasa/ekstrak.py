"""
===============================================================
 extract_existing_results.py
===============================================================
 Mengekstrak hasil evaluasi Rasa NLU yang SUDAH SELESAI dijalankan
 (dari eval_a.py atau eval_s.py) TANPA perlu mengulang proses
 training atau cross-validation.

 Skrip ini akan:
   - Membaca folder hasil (cv_run_1, cv_run_2, ..., train_test)
   - Menghitung rata-rata & SAMPLE standar deviasi (ddof=1)
   - Menampilkan ringkasan di konsol
   - Menyimpan file CSV ringkasan (extracted_summary.csv)
   - Menyimpan file CSV detail per kelas (extracted_detail.csv)

================================================================
 CARA PAKAI
================================================================
 1. Tentukan folder hasil Anda dengan mengubah variabel RESULTS_DIR
    di bawah. Contoh:

    a) Untuk mengekstrak SEMUA konfigurasi sekaligus (dari eval_a.py):
       RESULTS_DIR = "results/comparison_20260512_153045"

    b) Untuk mengekstrak SATU konfigurasi saja (misal baseline):
       RESULTS_DIR = "results/comparison_20260512_153045/CP_baseline"

    c) Untuk folder hasil single config (dari eval_s.py):
       RESULTS_DIR = "results/single_CP_baseline_20260512_153045"

 2. (Opsional) Ubah nama file CSV output dengan variabel OUTPUT_CSV.

 3. Jalankan skrip:
       python extract_existing_results.py

 4. Lihat hasil di konsol dan buka file CSV yang disimpan
    di dalam folder RESULTS_DIR.

================================================================
 CATATAN
================================================================
 - Skrip otomatis mendeteksi jumlah pengulangan CV (cv_run*)
   dan apakah ada data train_test (overfit detection).
 - Standar deviasi dihitung sebagai SAMPLE std (pembagi n-1),
   sesuai kaidah statistik inferensi untuk sampel kecil.
 - Tidak perlu training ulang, hanya membaca data yang sudah ada.
================================================================
"""

import os
import json
import csv
import glob
from statistics import mean, stdev

# ================================================================
# KONFIGURASI (ganti sesuai path folder hasil Anda)
# ================================================================
RESULTS_DIR = "results/comparison_20260512_145550"  # <-- GANTI INI
OUTPUT_CSV = "perbandingan.csv"  # akan disimpan di RESULTS_DIR
# ================================================================


def find_report_file(directory, pattern_suffix):
    """Cari file JSON laporan berdasarkan pola akhiran (misal '*intent_report.json')."""
    files = glob.glob(os.path.join(directory, f"*{pattern_suffix}"))
    return files[0] if files else None


def extract_full_metrics(results_dir):
    """
    Baca intent_report.json dan DIETClassifier_report.json,
    kembalikan dictionary berisi overall F1 dan per-class F1.
    """
    out = {
        "intent_f1": None,
        "entity_f1": None,
        "intent_per_class": {},
        "entity_per_class": {},
    }

    intent_file = find_report_file(results_dir, "intent_report.json")
    if intent_file:
        with open(intent_file, encoding="utf-8") as f:
            data = json.load(f)
        wavg = data.get("weighted avg", {})
        out["intent_f1"] = wavg.get("f1-score")
        for k, v in data.items():
            if (
                isinstance(v, dict)
                and "f1-score" in v
                and k not in ("macro avg", "weighted avg", "micro avg", "accuracy")
            ):
                out["intent_per_class"][k] = v["f1-score"]

    entity_file = find_report_file(results_dir, "DIETClassifier_report.json")
    if entity_file:
        with open(entity_file, encoding="utf-8") as f:
            data = json.load(f)
        wavg = data.get("weighted avg", {})
        out["entity_f1"] = wavg.get("f1-score")
        for k, v in data.items():
            if (
                isinstance(v, dict)
                and "f1-score" in v
                and k not in ("macro avg", "weighted avg", "micro avg", "accuracy")
            ):
                out["entity_per_class"][k] = v["f1-score"]

    return out


def compute_sample_stability(f1_values):
    """Hitung sample mean dan sample std (ddof=1)."""
    n = len(f1_values)
    if n == 0:
        return None, None
    avg = mean(f1_values)
    if n > 1:
        std = stdev(f1_values)  # sample std (ddof=1)
    else:
        std = 0.0
    return round(avg, 4), round(std, 4)


def per_class_stability(cv_runs, key):
    """
    Dari list folder cv_run, kumpulkan metric per kelas (dari key: 'intent_per_class' atau 'entity_per_class')
    lalu hitung mean & sample std untuk setiap kelas.
    """
    all_classes = set()
    for run_dir in cv_runs:
        metrics = extract_full_metrics(run_dir)
        all_classes.update(metrics.get(key, {}).keys())

    stability = {}
    for cls in sorted(all_classes):
        vals = []
        for run_dir in cv_runs:
            metrics = extract_full_metrics(run_dir)
            if cls in metrics.get(key, {}):
                vals.append(metrics[key][cls])
        if vals:
            mean_val, std_val = compute_sample_stability(vals)
            stability[cls] = (mean_val, std_val)
    return stability


def main():
    # Deteksi struktur folder
    configs = {}
    for entry in os.listdir(RESULTS_DIR):
        config_path = os.path.join(RESULTS_DIR, entry)
        if os.path.isdir(config_path):
            subdirs = os.listdir(config_path)
            if any(s.startswith("cv_run") or s == "train_test" for s in subdirs):
                configs[entry] = config_path

    if not configs:
        base = os.path.basename(RESULTS_DIR.rstrip("/\\"))
        configs[base] = RESULTS_DIR

    all_stability = []  # untuk overview
    config_per_class = {}  # config_label -> {"intent": {...}, "entity": {...}}

    for label, folder in configs.items():
        print(f"\nMemproses konfigurasi: {label}")

        cv_runs = sorted(glob.glob(os.path.join(folder, "cv_run*")))
        if not cv_runs:
            print("  ⚠ Tidak ada folder cv_run. Lewati.")
            continue

        intent_vals = []
        entity_vals = []
        for run_dir in cv_runs:
            metrics = extract_full_metrics(run_dir)
            if metrics["intent_f1"] is not None:
                intent_vals.append(metrics["intent_f1"])
            if metrics["entity_f1"] is not None:
                entity_vals.append(metrics["entity_f1"])

        intent_mean, intent_std = compute_sample_stability(intent_vals)
        entity_mean, entity_std = compute_sample_stability(entity_vals)

        # Per-class stability
        intent_class_stab = per_class_stability(cv_runs, "intent_per_class")
        entity_class_stab = per_class_stability(cv_runs, "entity_per_class")
        config_per_class[label] = {
            "intent": intent_class_stab,
            "entity": entity_class_stab,
        }

        # Train test (overfit detection)
        train_f1 = None
        train_test_dir = os.path.join(folder, "train_test")
        if os.path.isdir(train_test_dir):
            tt_metrics = extract_full_metrics(train_test_dir)
            train_f1 = tt_metrics["intent_f1"]

        print(f"  CV runs ditemukan: {len(cv_runs)}")
        print(f"  Intent F1 : {intent_mean} ± {intent_std}")
        print(f"  Entity F1 : {entity_mean} ± {entity_std}")
        if train_f1 is not None:
            gap = round(train_f1 - intent_mean, 4) if intent_mean else None
            print(f"  Training F1: {train_f1:.4f}  → gap: {gap}")

        all_stability.append(
            (
                label,
                intent_mean,
                intent_std,
                entity_mean,
                entity_std,
                train_f1,
                len(cv_runs),
            )
        )

    # --- Simpan overview CSV ---
    csv_path = os.path.join(RESULTS_DIR, OUTPUT_CSV)
    fieldnames = [
        "config",
        "intent_f1_mean",
        "intent_f1_std",
        "entity_f1_mean",
        "entity_f1_std",
        "train_intent_f1",
        "gap(train-cv)",
        "status_overfit",
        "num_cv_runs",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for label, i_mean, i_std, e_mean, e_std, train_f1, num_cv in all_stability:
            gap = (
                round(train_f1 - i_mean, 4)
                if (train_f1 is not None and i_mean is not None)
                else ""
            )
            if gap != "":
                if gap > 0.15:
                    verdict = "OVERFIT"
                elif gap > 0.05:
                    verdict = "SEDIKIT OVERFIT"
                else:
                    verdict = "GENERALISASI BAIK"
            else:
                verdict = "tidak ada data train_test"

            writer.writerow(
                {
                    "config": label,
                    "intent_f1_mean": i_mean,
                    "intent_f1_std": i_std,
                    "entity_f1_mean": e_mean,
                    "entity_f1_std": e_std,
                    "train_intent_f1": round(train_f1, 4) if train_f1 else "",
                    "gap(train-cv)": gap,
                    "status_overfit": verdict,
                    "num_cv_runs": num_cv,
                }
            )

    print(f"\n✅ Ringkasan disimpan ke: {csv_path}")

    # --- Simpan detail CSV (per kelas) ---
    detail_csv = os.path.join(RESULTS_DIR, "detail perbandingan.csv")
    all_intents = set()
    all_entities = set()
    for label, data in config_per_class.items():
        all_intents.update(data["intent"].keys())
        all_entities.update(data["entity"].keys())

    detail_rows = []
    for cls_type, classes, key in [
        ("intent", sorted(all_intents), "intent"),
        ("entity", sorted(all_entities), "entity"),
    ]:
        for cls_name in classes:
            row = {"type": cls_type, "class": cls_name}
            for label, data in config_per_class.items():
                stab = data[key].get(cls_name)
                if stab:
                    mean_val, std_val = stab
                    row[f"{label}_f1"] = mean_val
                    row[f"{label}_std"] = std_val
                else:
                    row[f"{label}_f1"] = ""
                    row[f"{label}_std"] = ""
            detail_rows.append(row)

    detail_fieldnames = ["type", "class"]
    for label in config_per_class.keys():
        detail_fieldnames += [f"{label}_f1", f"{label}_std"]

    with open(detail_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=detail_fieldnames)
        writer.writeheader()
        writer.writerows(detail_rows)
    print(f"✅ Detail per kelas disimpan ke: {detail_csv}")

    # Tampilkan tabel perbandingan (jika multi config)
    if len(all_stability) > 1:
        print(f"\n{'='*80}")
        print("PERBANDINGAN SELURUH KONFIGURASI")
        print(f"{'='*80}")
        header = f"{'Config':<20} {'Int F1':>8} {'±':>6} {'Ent F1':>8} {'±':>6} {'Train F1':>8} {'Gap':>7} {'Status'}"
        print(header)
        print("-" * 80)
        for label, i_mean, i_std, e_mean, e_std, train_f1, _ in all_stability:
            gap = round(train_f1 - i_mean, 4) if (train_f1 and i_mean) else 0.0
            if train_f1:
                if gap > 0.15:
                    v = "OVERFIT"
                elif gap > 0.05:
                    v = "SEDIKIT OVERFIT"
                else:
                    v = "GOOD FIT"
            else:
                v = "N/A"
            print(
                f"{label:<20} {i_mean:>8.4f} {i_std:>6.4f} {e_mean:>8.4f} {e_std:>6.4f} "
                f"{train_f1 if train_f1 else 'N/A':>8} {gap:>7.4f}  {v}"
            )


if __name__ == "__main__":
    main()
