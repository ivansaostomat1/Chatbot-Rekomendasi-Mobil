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
RESULTS_DIR = "results/baru"  # <-- GANTI INI
OUTPUT_CSV = "comparison_overview.csv"  # akan disimpan di RESULTS_DIR
# ================================================================


def find_report_file(directory, pattern_suffix):
    """Cari file JSON laporan berdasarkan pola akhiran (misal '*intent_report.json')."""
    files = glob.glob(os.path.join(directory, f"*{pattern_suffix}"))
    return files[0] if files else None


def extract_full_metrics(results_dir):
    """
    Baca intent_report.json dan DIETClassifier_report.json,
    kembalikan dictionary berisi overall F1, Precision, Recall dan per-class.
    """
    out = {
        "intent_f1": None,
        "intent_precision": None,
        "intent_recall": None,
        "entity_f1": None,
        "entity_precision": None,
        "entity_recall": None,
        "intent_per_class": {},
        "intent_per_class_precision": {},
        "intent_per_class_recall": {},
        "entity_per_class": {},
        "entity_per_class_precision": {},
        "entity_per_class_recall": {},
    }

    intent_file = find_report_file(results_dir, "intent_report.json")
    if intent_file:
        with open(intent_file, encoding="utf-8") as f:
            data = json.load(f)
        wavg = data.get("weighted avg", {})
        out["intent_f1"] = wavg.get("f1-score")
        out["intent_precision"] = wavg.get("precision")
        out["intent_recall"] = wavg.get("recall")
        for k, v in data.items():
            if (
                isinstance(v, dict)
                and "f1-score" in v
                and k not in ("macro avg", "weighted avg", "micro avg", "accuracy")
            ):
                out["intent_per_class"][k] = v["f1-score"]
                out["intent_per_class_precision"][k] = v.get("precision", 0)
                out["intent_per_class_recall"][k] = v.get("recall", 0)

    entity_file = find_report_file(results_dir, "DIETClassifier_report.json")
    if entity_file:
        with open(entity_file, encoding="utf-8") as f:
            data = json.load(f)
        wavg = data.get("weighted avg", {})
        out["entity_f1"] = wavg.get("f1-score")
        out["entity_precision"] = wavg.get("precision")
        out["entity_recall"] = wavg.get("recall")
        for k, v in data.items():
            if (
                isinstance(v, dict)
                and "f1-score" in v
                and k not in ("macro avg", "weighted avg", "micro avg", "accuracy")
            ):
                out["entity_per_class"][k] = v["f1-score"]
                out["entity_per_class_precision"][k] = v.get("precision", 0)
                out["entity_per_class_recall"][k] = v.get("recall", 0)

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


def save_single_config_csv(label, folder, overall_data, per_class_data):
    """
    Simpan CSV ringkasan dan detail per-kelas untuk SATU konfigurasi
    ke dalam folder konfigurasi itu sendiri.
    """
    (
        _label,
        i_f1_m, i_f1_s,
        i_p_m, i_p_s,
        i_r_m, i_r_s,
        e_f1_m, e_f1_s,
        e_p_m, e_p_s,
        e_r_m, e_r_s,
        train_f1,
        num_cv,
    ) = overall_data

    # --- Ringkasan overview ---
    overview_path = os.path.join(folder, f"{label}_perbandingan.csv")
    gap = (
        round(train_f1 - i_f1_m, 4)
        if (train_f1 is not None and i_f1_m is not None)
        else ""
    )
    if gap != "":
        if gap > 0.15:
            verdict = "OVERFIT"
        elif gap > 0.05:
            verdict = "SEDIKIT OVERFIT"
        else:
            verdict = "GOOD FIT"
    else:
        verdict = "tidak ada data train_test"

    fieldnames = [
        "config",
        "intent_f1_mean", "intent_f1_std",
        "intent_precision_mean", "intent_precision_std",
        "intent_recall_mean", "intent_recall_std",
        "entity_f1_mean", "entity_f1_std",
        "entity_precision_mean", "entity_precision_std",
        "entity_recall_mean", "entity_recall_std",
        "train_intent_f1", "gap(train-cv)", "status_overfit", "num_cv_runs",
    ]
    with open(overview_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({
            "config": label,
            "intent_f1_mean": i_f1_m, "intent_f1_std": i_f1_s,
            "intent_precision_mean": i_p_m, "intent_precision_std": i_p_s,
            "intent_recall_mean": i_r_m, "intent_recall_std": i_r_s,
            "entity_f1_mean": e_f1_m, "entity_f1_std": e_f1_s,
            "entity_precision_mean": e_p_m, "entity_precision_std": e_p_s,
            "entity_recall_mean": e_r_m, "entity_recall_std": e_r_s,
            "train_intent_f1": round(train_f1, 4) if train_f1 else "",
            "gap(train-cv)": gap,
            "status_overfit": verdict,
            "num_cv_runs": num_cv,
        })
    print(f"    [CSV] {overview_path}")

    # --- Detail per kelas ---
    detail_path = os.path.join(folder, f"{label}_detail_perbandingan.csv")
    detail_fieldnames = [
        "type", "class",
        f"{label}_f1", f"{label}_f1_std",
        f"{label}_precision", f"{label}_precision_std",
        f"{label}_recall", f"{label}_recall_std",
    ]
    detail_rows = []
    for cls_type, f1_key, prec_key, rec_key in [
        ("intent", "intent", "intent_precision", "intent_recall"),
        ("entity", "entity", "entity_precision", "entity_recall"),
    ]:
        all_classes = set(per_class_data[f1_key].keys())
        for cls_name in sorted(all_classes):
            row = {"type": cls_type, "class": cls_name}
            for metric_key, suffix in [
                (f1_key, "f1"), (prec_key, "precision"), (rec_key, "recall"),
            ]:
                stab = per_class_data[metric_key].get(cls_name)
                if stab:
                    row[f"{label}_{suffix}"] = stab[0]
                    row[f"{label}_{suffix}_std"] = stab[1]
                else:
                    row[f"{label}_{suffix}"] = ""
                    row[f"{label}_{suffix}_std"] = ""
            detail_rows.append(row)

    with open(detail_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=detail_fieldnames)
        writer.writeheader()
        writer.writerows(detail_rows)
    print(f"    [CSV] {detail_path}")


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
    config_per_class = {}  # config_label -> {"intent": {...}, ...}

    for label, folder in configs.items():
        print(f"\nMemproses konfigurasi: {label}")

        cv_runs = sorted(glob.glob(os.path.join(folder, "cv_run*")))
        if not cv_runs:
            print("  [!] Tidak ada folder cv_run. Lewati.")
            continue

        intent_f1_vals = []
        intent_prec_vals = []
        intent_rec_vals = []
        entity_f1_vals = []
        entity_prec_vals = []
        entity_rec_vals = []
        for run_dir in cv_runs:
            metrics = extract_full_metrics(run_dir)
            if metrics["intent_f1"] is not None:
                intent_f1_vals.append(metrics["intent_f1"])
            if metrics["intent_precision"] is not None:
                intent_prec_vals.append(metrics["intent_precision"])
            if metrics["intent_recall"] is not None:
                intent_rec_vals.append(metrics["intent_recall"])
            if metrics["entity_f1"] is not None:
                entity_f1_vals.append(metrics["entity_f1"])
            if metrics["entity_precision"] is not None:
                entity_prec_vals.append(metrics["entity_precision"])
            if metrics["entity_recall"] is not None:
                entity_rec_vals.append(metrics["entity_recall"])

        intent_f1_mean, intent_f1_std = compute_sample_stability(intent_f1_vals)
        intent_prec_mean, intent_prec_std = compute_sample_stability(intent_prec_vals)
        intent_rec_mean, intent_rec_std = compute_sample_stability(intent_rec_vals)
        entity_f1_mean, entity_f1_std = compute_sample_stability(entity_f1_vals)
        entity_prec_mean, entity_prec_std = compute_sample_stability(entity_prec_vals)
        entity_rec_mean, entity_rec_std = compute_sample_stability(entity_rec_vals)

        # Per-class stability (F1, Precision, Recall)
        intent_class_stab = per_class_stability(cv_runs, "intent_per_class")
        intent_class_prec_stab = per_class_stability(cv_runs, "intent_per_class_precision")
        intent_class_rec_stab = per_class_stability(cv_runs, "intent_per_class_recall")
        entity_class_stab = per_class_stability(cv_runs, "entity_per_class")
        entity_class_prec_stab = per_class_stability(cv_runs, "entity_per_class_precision")
        entity_class_rec_stab = per_class_stability(cv_runs, "entity_per_class_recall")
        config_per_class[label] = {
            "intent": intent_class_stab,
            "intent_precision": intent_class_prec_stab,
            "intent_recall": intent_class_rec_stab,
            "entity": entity_class_stab,
            "entity_precision": entity_class_prec_stab,
            "entity_recall": entity_class_rec_stab,
        }

        # Train test (overfit detection)
        train_f1 = None
        train_test_dir = os.path.join(folder, "train_test")
        if os.path.isdir(train_test_dir):
            tt_metrics = extract_full_metrics(train_test_dir)
            train_f1 = tt_metrics["intent_f1"]

        print(f"  CV runs ditemukan: {len(cv_runs)}")
        print(f"  Intent F1        : {intent_f1_mean} ± {intent_f1_std}")
        print(f"  Intent Precision : {intent_prec_mean} ± {intent_prec_std}")
        print(f"  Intent Recall    : {intent_rec_mean} ± {intent_rec_std}")
        print(f"  Entity F1        : {entity_f1_mean} ± {entity_f1_std}")
        print(f"  Entity Precision : {entity_prec_mean} ± {entity_prec_std}")
        print(f"  Entity Recall    : {entity_rec_mean} ± {entity_rec_std}")
        if train_f1 is not None:
            gap = round(train_f1 - intent_f1_mean, 4) if intent_f1_mean else None
            print(f"  Training F1: {train_f1:.4f}  -> gap: {gap}")

        overall_tuple = (
            label,
            intent_f1_mean,
            intent_f1_std,
            intent_prec_mean,
            intent_prec_std,
            intent_rec_mean,
            intent_rec_std,
            entity_f1_mean,
            entity_f1_std,
            entity_prec_mean,
            entity_prec_std,
            entity_rec_mean,
            entity_rec_std,
            train_f1,
            len(cv_runs),
        )
        all_stability.append(overall_tuple)

        # Simpan CSV per config ke folder masing-masing
        if folder != RESULTS_DIR:  # hanya jika multi-config
            print(f"  Menyimpan CSV per-config:")
            save_single_config_csv(label, folder, overall_tuple, config_per_class[label])

    # --- Simpan overview CSV ---
    csv_path = os.path.join(RESULTS_DIR, "comparison_overview.csv")
    fieldnames = [
        "config",
        "intent_f1_mean",
        "intent_f1_std",
        "intent_precision_mean",
        "intent_precision_std",
        "intent_recall_mean",
        "intent_recall_std",
        "entity_f1_mean",
        "entity_f1_std",
        "entity_precision_mean",
        "entity_precision_std",
        "entity_recall_mean",
        "entity_recall_std",
        "train_intent_f1",
        "gap(train-cv)",
        "status_overfit",
        "num_cv_runs",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for (
            label,
            i_f1_m, i_f1_s,
            i_p_m, i_p_s,
            i_r_m, i_r_s,
            e_f1_m, e_f1_s,
            e_p_m, e_p_s,
            e_r_m, e_r_s,
            train_f1,
            num_cv,
        ) in all_stability:
            gap = (
                round(train_f1 - i_f1_m, 4)
                if (train_f1 is not None and i_f1_m is not None)
                else ""
            )
            if gap != "":
                if gap > 0.15:
                    verdict = "OVERFIT"
                elif gap > 0.05:
                    verdict = "SEDIKIT OVERFIT"
                else:
                    verdict = "GOOD FIT"
            else:
                verdict = "tidak ada data train_test"

            writer.writerow(
                {
                    "config": label,
                    "intent_f1_mean": i_f1_m,
                    "intent_f1_std": i_f1_s,
                    "intent_precision_mean": i_p_m,
                    "intent_precision_std": i_p_s,
                    "intent_recall_mean": i_r_m,
                    "intent_recall_std": i_r_s,
                    "entity_f1_mean": e_f1_m,
                    "entity_f1_std": e_f1_s,
                    "entity_precision_mean": e_p_m,
                    "entity_precision_std": e_p_s,
                    "entity_recall_mean": e_r_m,
                    "entity_recall_std": e_r_s,
                    "train_intent_f1": round(train_f1, 4) if train_f1 else "",
                    "gap(train-cv)": gap,
                    "status_overfit": verdict,
                    "num_cv_runs": num_cv,
                }
            )

    print(f"\n[OK] Ringkasan disimpan ke: {csv_path}")

    # --- Simpan detail CSV (per kelas) ---
    detail_csv = os.path.join(RESULTS_DIR, "comparison_detail.csv")
    all_intents = set()
    all_entities = set()
    for label, data in config_per_class.items():
        all_intents.update(data["intent"].keys())
        all_entities.update(data["entity"].keys())

    detail_rows = []
    for cls_type, classes, f1_key, prec_key, rec_key in [
        ("intent", sorted(all_intents), "intent", "intent_precision", "intent_recall"),
        ("entity", sorted(all_entities), "entity", "entity_precision", "entity_recall"),
    ]:
        for cls_name in classes:
            row = {"type": cls_type, "class": cls_name}
            for label, data in config_per_class.items():
                # F1
                stab = data[f1_key].get(cls_name)
                if stab:
                    mean_val, std_val = stab
                    row[f"{label}_f1"] = mean_val
                    row[f"{label}_f1_std"] = std_val
                else:
                    row[f"{label}_f1"] = ""
                    row[f"{label}_f1_std"] = ""
                # Precision
                stab_p = data[prec_key].get(cls_name)
                if stab_p:
                    mean_val, std_val = stab_p
                    row[f"{label}_precision"] = mean_val
                    row[f"{label}_precision_std"] = std_val
                else:
                    row[f"{label}_precision"] = ""
                    row[f"{label}_precision_std"] = ""
                # Recall
                stab_r = data[rec_key].get(cls_name)
                if stab_r:
                    mean_val, std_val = stab_r
                    row[f"{label}_recall"] = mean_val
                    row[f"{label}_recall_std"] = std_val
                else:
                    row[f"{label}_recall"] = ""
                    row[f"{label}_recall_std"] = ""
            detail_rows.append(row)

    detail_fieldnames = ["type", "class"]
    for label in config_per_class.keys():
        detail_fieldnames += [
            f"{label}_f1", f"{label}_f1_std",
            f"{label}_precision", f"{label}_precision_std",
            f"{label}_recall", f"{label}_recall_std",
        ]

    with open(detail_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=detail_fieldnames)
        writer.writeheader()
        writer.writerows(detail_rows)
    print(f"[OK] Detail per kelas disimpan ke: {detail_csv}")

    # Tampilkan tabel perbandingan (jika multi config)
    if len(all_stability) > 1:
        print(f"\n{'='*100}")
        print("PERBANDINGAN SELURUH KONFIGURASI")
        print(f"{'='*100}")
        header = (
            f"{'Config':<20} {'Int F1':>8} {'±':>6} {'Int Prec':>8} {'Int Rec':>8} "
            f"{'Ent F1':>8} {'±':>6} {'Ent Prec':>8} {'Ent Rec':>8} "
            f"{'Train F1':>8} {'Gap':>7} {'Status'}"
        )
        print(header)
        print("-" * 100)
        for (
            label,
            i_f1_m, i_f1_s,
            i_p_m, i_p_s,
            i_r_m, i_r_s,
            e_f1_m, e_f1_s,
            e_p_m, e_p_s,
            e_r_m, e_r_s,
            train_f1,
            _,
        ) in all_stability:
            gap = round(train_f1 - i_f1_m, 4) if (train_f1 and i_f1_m) else 0.0
            if train_f1:
                if gap > 0.15:
                    v = "OVERFIT"
                elif gap > 0.05:
                    v = "SEDIKIT OVERFIT"
                else:
                    v = "GOOD FIT"
            else:
                v = "N/A"
            i_p_val = f"{i_p_m:.4f}" if i_p_m is not None else "N/A"
            i_r_val = f"{i_r_m:.4f}" if i_r_m is not None else "N/A"
            e_p_val = f"{e_p_m:.4f}" if e_p_m is not None else "N/A"
            e_r_val = f"{e_r_m:.4f}" if e_r_m is not None else "N/A"
            print(
                f"{label:<20} {i_f1_m:>8.4f} {i_f1_s:>6.4f} {i_p_val:>8} {i_r_val:>8} "
                f"{e_f1_m:>8.4f} {e_f1_s:>6.4f} {e_p_val:>8} {e_r_val:>8} "
                f"{train_f1 if train_f1 else 'N/A':>8} {gap:>7.4f}  {v}"
            )


if __name__ == "__main__":
    main()
