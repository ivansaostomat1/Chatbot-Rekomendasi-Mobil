import subprocess
import os
import datetime
import json
import csv
import sys
import time
import glob   # <-- tambahan

# ================================================================
# KONFIGURASI — ubah di sini kalau perlu
# ================================================================
NLU_DATA_PATH = "data/nlu.yml"
MODELS_DIR = "models"
N_RUNS = 3
FOLDS = 5

CONFIGS = [
    ("Default", "configDefault.yml"),
    ("TAv1", "configTAv1.yml"),
    ("TAv2", "configTAv2.yml"),
    ("TAv3", "configTAv3.yml"),
    ("TAv4", "configTAv4.yml"),
    ("TAv5", "configTAv5.yml"),
    ("TAv6", "configTAv6.yml"),
]
# ================================================================


def run_command(command, description, log_file=None):
    print(f"\n{'='*60}")
    print(f"Running : {description}")
    print(f"Command : {' '.join(command)}")
    print(f"{'='*60}\n")
    try:
        result = subprocess.run(
            command,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if log_file:
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(result.stdout)
        print(result.stdout[-3000:])
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {description} gagal (exit code {e.returncode})")
        if e.output:
            print(e.output[-2000:])
        if log_file:
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(e.output or "")
        return False
    except Exception as e:
        print(f"ERROR tidak terduga: {e}")
        return False


def extract_f1_summary(results_dir):
    summary = {}

    intent_path = os.path.join(results_dir, "intent_report.json")
    if os.path.exists(intent_path):
        with open(intent_path, encoding="utf-8") as f:
            data = json.load(f)
        wavg = data.get("weighted avg", {})
        summary["intent_overall_f1"] = wavg.get("f1-score")
        summary["intent_overall_precision"] = wavg.get("precision")
        summary["intent_overall_recall"] = wavg.get("recall")
        summary["intent_overall_acc"] = data.get("accuracy")
        summary["intent_per_class"] = {}
        summary["intent_per_class_precision"] = {}
        summary["intent_per_class_recall"] = {}
        for k, v in data.items():
            if (
                isinstance(v, dict)
                and "f1-score" in v
                and k not in ("macro avg", "weighted avg", "micro avg")
            ):
                summary["intent_per_class"][k] = round(v["f1-score"], 4)
                summary["intent_per_class_precision"][k] = round(v.get("precision", 0), 4)
                summary["intent_per_class_recall"][k] = round(v.get("recall", 0), 4)

    entity_path = os.path.join(results_dir, "DIETClassifier_report.json")
    if os.path.exists(entity_path):
        with open(entity_path, encoding="utf-8") as f:
            data = json.load(f)
        wavg = data.get("weighted avg", {})
        summary["entity_overall_f1"] = wavg.get("f1-score")
        summary["entity_overall_precision"] = wavg.get("precision")
        summary["entity_overall_recall"] = wavg.get("recall")
        summary["entity_per_class"] = {}
        summary["entity_per_class_precision"] = {}
        summary["entity_per_class_recall"] = {}
        for k, v in data.items():
            if (
                isinstance(v, dict)
                and "f1-score" in v
                and k not in ("macro avg", "weighted avg", "micro avg")
            ):
                summary["entity_per_class"][k] = round(v["f1-score"], 4)
                summary["entity_per_class_precision"][k] = round(v.get("precision", 0), 4)
                summary["entity_per_class_recall"][k] = round(v.get("recall", 0), 4)

    return summary


def rename_outputs(results_dir, config_label, run_label):
    prefix = f"{config_label}_{run_label}_"
    targets = [
        "intent_report.json",
        "intent_errors.json",
        "intent_histogram.png",
        "intent_confusion_matrix.png",
        "DIETClassifier_report.json",
        "DIETClassifier_errors.json",
        "DIETClassifier_confusion_matrix.png",
        "response_selection_report.json",
        "response_selection_errors.json",
        "output.log",
    ]
    renamed = []
    for filename in targets:
        src = os.path.join(results_dir, filename)
        if os.path.exists(src):
            dst = os.path.join(results_dir, prefix + filename)
            os.rename(src, dst)
            renamed.append(prefix + filename)
    if renamed:
        print(f"  Renamed {len(renamed)} file(s) → prefix '{prefix}'")


def compute_stability(summaries):
    result = {}

    def mean_std(vals):
        if not vals:
            return None, None
        mean = sum(vals) / len(vals)
        if len(vals) > 1:
            variance = sum((x - mean) ** 2 for x in vals) / (len(vals) - 1)
            std = variance ** 0.5
        else:
            std = 0.0
        return round(mean, 4), round(std, 4)

    def overall_stab(key, prefix):
        vals = [s[key] for s in summaries if key in s and s[key] is not None]
        m, s = mean_std(vals)
        if m is not None:
            result[f"{prefix}_mean"] = m
            result[f"{prefix}_std"] = s

    def per_class_stab(key, prefix):
        all_classes = set()
        for s in summaries:
            all_classes.update(s.get(key, {}).keys())
        result[prefix] = {}
        for cls in sorted(all_classes):
            vals = [
                s[key][cls]
                for s in summaries
                if cls in s.get(key, {})
            ]
            m, sd = mean_std(vals)
            if m is not None:
                result[prefix][cls] = (m, sd)

    # Intent — F1, Precision, Recall
    overall_stab("intent_overall_f1", "intent_overall")
    overall_stab("intent_overall_precision", "intent_overall_precision")
    overall_stab("intent_overall_recall", "intent_overall_recall")
    per_class_stab("intent_per_class", "intent_per_class")
    per_class_stab("intent_per_class_precision", "intent_per_class_precision")
    per_class_stab("intent_per_class_recall", "intent_per_class_recall")

    # Entity — F1, Precision, Recall
    overall_stab("entity_overall_f1", "entity_overall")
    overall_stab("entity_overall_precision", "entity_overall_precision")
    overall_stab("entity_overall_recall", "entity_overall_recall")
    per_class_stab("entity_per_class", "entity_per_class")
    per_class_stab("entity_per_class_precision", "entity_per_class_precision")
    per_class_stab("entity_per_class_recall", "entity_per_class_recall")

    return result


def print_stability(label, stab, train_f1=None):
    print(f"\n{'='*60}")
    print(f"HASIL: {label}")
    print(f"{'='*60}")

    if "intent_overall_mean" in stab:
        f1 = stab["intent_overall_mean"]
        std = stab["intent_overall_std"]
        prec = stab.get("intent_overall_precision_mean")
        prec_std = stab.get("intent_overall_precision_std")
        rec = stab.get("intent_overall_recall_mean")
        rec_std = stab.get("intent_overall_recall_std")
        print(f"\n  [INTENT] Overall F1        : {f1:.4f} ± {std:.4f}")
        if prec is not None:
            print(f"           Overall Precision : {prec:.4f} ± {prec_std:.4f}")
        if rec is not None:
            print(f"           Overall Recall    : {rec:.4f} ± {rec_std:.4f}")
        if train_f1 is not None:
            gap = train_f1 - f1
            if gap > 0.15:
                verdict = "OVERFIT"
            elif gap > 0.05:
                verdict = "SEDIKIT OVERFIT (wajar untuk dataset kecil)"
            else:
                verdict = "GOOD FIT"
            print(
                f"           Training F1: {train_f1:.4f}  |  Gap: {gap:.4f}  →  {verdict}"
            )

        print(f"\n  Intent per class (mean ± std):")
        print(f"    {'Kelas':<30} {'F1':>12} {'Precision':>12} {'Recall':>12}  Flags")
        print(f"    {'-'*30} {'-'*12} {'-'*12} {'-'*12}  {'-'*15}")
        for intent, (mean, std) in stab.get("intent_per_class", {}).items():
            p = stab.get("intent_per_class_precision", {}).get(intent)
            r = stab.get("intent_per_class_recall", {}).get(intent)
            p_str = f"{p[0]:.4f}±{p[1]:.4f}" if p else "N/A"
            r_str = f"{r[0]:.4f}±{r[1]:.4f}" if r else "N/A"
            flags = []
            if mean < 0.80:
                flags.append("LEMAH")
            if std > 0.05:
                flags.append("TIDAK STABIL")
            flag_str = "  <-- " + ", ".join(flags) if flags else ""
            print(f"    {intent:<30} {mean:.4f}±{std:.4f} {p_str:>12} {r_str:>12}{flag_str}")

    if "entity_overall_mean" in stab:
        f1 = stab["entity_overall_mean"]
        std = stab["entity_overall_std"]
        prec = stab.get("entity_overall_precision_mean")
        prec_std = stab.get("entity_overall_precision_std")
        rec = stab.get("entity_overall_recall_mean")
        rec_std = stab.get("entity_overall_recall_std")
        print(f"\n  [ENTITY] Overall F1        : {f1:.4f} ± {std:.4f}")
        if prec is not None:
            print(f"           Overall Precision : {prec:.4f} ± {prec_std:.4f}")
        if rec is not None:
            print(f"           Overall Recall    : {rec:.4f} ± {rec_std:.4f}")

        print(f"\n  Entity per class (mean ± std):")
        print(f"    {'Kelas':<30} {'F1':>12} {'Precision':>12} {'Recall':>12}  Flags")
        print(f"    {'-'*30} {'-'*12} {'-'*12} {'-'*12}  {'-'*15}")
        for entity, (mean, std) in stab.get("entity_per_class", {}).items():
            p = stab.get("entity_per_class_precision", {}).get(entity)
            r = stab.get("entity_per_class_recall", {}).get(entity)
            p_str = f"{p[0]:.4f}±{p[1]:.4f}" if p else "N/A"
            r_str = f"{r[0]:.4f}±{r[1]:.4f}" if r else "N/A"
            flags = []
            if mean < 0.70:
                flags.append("LEMAH")
            if std > 0.05:
                flags.append("TIDAK STABIL")
            flag_str = "  <-- " + ", ".join(flags) if flags else ""
            print(f"    {entity:<30} {mean:.4f}±{std:.4f} {p_str:>12} {r_str:>12}{flag_str}")


def save_comparison_csv(all_results, session_dir):
    overview_path = os.path.join(session_dir, "comparison_overview.csv")
    overview_rows = []
    for config_label, stab, train_f1, cv_dur, train_dur in all_results:
        intent_f1 = stab.get("intent_overall_mean", "")
        intent_std = stab.get("intent_overall_std", "")
        intent_prec = stab.get("intent_overall_precision_mean", "")
        intent_prec_std = stab.get("intent_overall_precision_std", "")
        intent_rec = stab.get("intent_overall_recall_mean", "")
        intent_rec_std = stab.get("intent_overall_recall_std", "")
        entity_f1 = stab.get("entity_overall_mean", "")
        entity_std = stab.get("entity_overall_std", "")
        entity_prec = stab.get("entity_overall_precision_mean", "")
        entity_prec_std = stab.get("entity_overall_precision_std", "")
        entity_rec = stab.get("entity_overall_recall_mean", "")
        entity_rec_std = stab.get("entity_overall_recall_std", "")
        gap = round(train_f1 - intent_f1, 4) if (train_f1 and intent_f1) else ""
        if gap != "":
            if gap > 0.15:
                verdict = "OVERFIT"
            elif gap > 0.05:
                verdict = "SEDIKIT OVERFIT"
            else:
                verdict = "GOOD FIT"
        else:
            verdict = ""
        overview_rows.append(
            {
                "config": config_label,
                "intent_f1_mean": intent_f1,
                "intent_f1_std": intent_std,
                "intent_precision_mean": intent_prec,
                "intent_precision_std": intent_prec_std,
                "intent_recall_mean": intent_rec,
                "intent_recall_std": intent_rec_std,
                "intent_train_f1": round(train_f1, 4) if train_f1 else "",
                "gap_train_vs_cv": gap,
                "overfit_verdict": verdict,
                "entity_f1_mean": entity_f1,
                "entity_f1_std": entity_std,
                "entity_precision_mean": entity_prec,
                "entity_precision_std": entity_prec_std,
                "entity_recall_mean": entity_rec,
                "entity_recall_std": entity_rec_std,
                "cv_duration_seconds": cv_dur,
                "train_duration_seconds": train_dur,
            }
        )

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
        "intent_train_f1",
        "gap_train_vs_cv",
        "overfit_verdict",
        "cv_duration_seconds",
        "train_duration_seconds",
    ]
    with open(overview_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(overview_rows)
    print(f"\n  Saved: {overview_path}")

    # Detail per class
    all_intent_labels = set()
    all_entity_labels = set()
    for config_label, stab, _, _, _ in all_results:
        all_intent_labels.update(stab.get("intent_per_class", {}).keys())
        all_entity_labels.update(stab.get("entity_per_class", {}).keys())

    detail_path = os.path.join(session_dir, "comparison_detail.csv")
    detail_rows = []

    for class_type, labels, f1_key, prec_key, rec_key in [
        ("intent", sorted(all_intent_labels), "intent_per_class", "intent_per_class_precision", "intent_per_class_recall"),
        ("entity", sorted(all_entity_labels), "entity_per_class", "entity_per_class_precision", "entity_per_class_recall"),
    ]:
        for label in labels:
            row = {"type": class_type, "class": label}
            for config_label, stab, _, _, _ in all_results:
                # F1
                f1_data = stab.get(f1_key, {})
                if label in f1_data:
                    mean, std = f1_data[label]
                    row[f"{config_label}_f1"] = mean
                    row[f"{config_label}_f1_std"] = std
                else:
                    row[f"{config_label}_f1"] = ""
                    row[f"{config_label}_f1_std"] = ""
                # Precision
                p_data = stab.get(prec_key, {})
                if label in p_data:
                    mean, std = p_data[label]
                    row[f"{config_label}_precision"] = mean
                    row[f"{config_label}_precision_std"] = std
                else:
                    row[f"{config_label}_precision"] = ""
                    row[f"{config_label}_precision_std"] = ""
                # Recall
                r_data = stab.get(rec_key, {})
                if label in r_data:
                    mean, std = r_data[label]
                    row[f"{config_label}_recall"] = mean
                    row[f"{config_label}_recall_std"] = std
                else:
                    row[f"{config_label}_recall"] = ""
                    row[f"{config_label}_recall_std"] = ""
            detail_rows.append(row)

    fieldnames = ["type", "class"]
    for config_label, _, _, _, _ in all_results:
        fieldnames += [
            f"{config_label}_f1", f"{config_label}_f1_std",
            f"{config_label}_precision", f"{config_label}_precision_std",
            f"{config_label}_recall", f"{config_label}_recall_std",
        ]

    with open(detail_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(detail_rows)
    print(f"  Saved: {detail_path}")


def run_config(config_label, config_path, session_dir):
    config_dir = os.path.join(session_dir, config_label)
    os.makedirs(config_dir, exist_ok=True)

    print(f"\n\n{'#'*60}")
    print(f"# CONFIG : {config_label}")
    print(f"# File   : {config_path}")
    print(f"{'#'*60}")

    # ---------- CV ----------
    cv_start = time.time()
    cv_summaries = []
    for run_idx in range(1, N_RUNS + 1):
        cv_dir = os.path.join(config_dir, f"cv_run{run_idx}")
        os.makedirs(cv_dir, exist_ok=True)
        print(f"\n  [CV {run_idx}/{N_RUNS}] {config_label}")
        success = run_command(
            command=[
                "rasa", "test", "nlu",
                "--nlu", NLU_DATA_PATH,
                "--config", config_path,
                "--cross-validation",
                "--folds", str(FOLDS),
                "--out", cv_dir,
            ],
            description=f"{config_label} — CV Run {run_idx}/{N_RUNS}",
            log_file=os.path.join(cv_dir, "output.log"),
        )
        if success:
            cv_summaries.append(extract_f1_summary(cv_dir))
            rename_outputs(cv_dir, config_label, f"cv_run{run_idx}")
        else:
            print(f"  CV Run {run_idx} gagal.")
    cv_end = time.time()
    cv_duration = round(cv_end - cv_start, 2)
    print(f"\n  >>> Total Durasi CV ({N_RUNS} runs): {cv_duration} detik")

    stab = compute_stability(cv_summaries) if cv_summaries else {}

    # ---------- Training + Overfit ----------
    train_start = time.time()
    train_f1 = None
    print(f"\n  [TRAIN] {config_label}")
    train_ok = run_command(
        command=["rasa", "train", "nlu", "--config", config_path],
        description=f"{config_label} — Training",
        log_file=os.path.join(config_dir, f"{config_label}_train_output.log"),
    )
    if train_ok:
        # Cari model terbaru yang baru dibuat
        model_candidates = glob.glob(os.path.join(MODELS_DIR, "nlu-*.tar.gz"))
        if model_candidates:
            latest_model = max(model_candidates, key=os.path.getctime)
            tt_dir = os.path.join(config_dir, "train_test")
            os.makedirs(tt_dir, exist_ok=True)
            tt_ok = run_command(
                command=[
                    "rasa", "test", "nlu",
                    "--nlu", NLU_DATA_PATH,
                    "--config", config_path,
                    "--model", latest_model,   # <-- gunakan path model spesifik
                    "--out", tt_dir,
                ],
                description=f"{config_label} — Overfit Detection",
                log_file=os.path.join(tt_dir, "output.log"),
            )
            if tt_ok:
                tt_summary = extract_f1_summary(tt_dir)
                train_f1 = tt_summary.get("intent_overall_f1")
                rename_outputs(tt_dir, config_label, "train_test")
        else:
            print("  Model tidak ditemukan setelah training.")
    train_end = time.time()
    train_duration = round(train_end - train_start, 2)
    print(f"  >>> Total Durasi Training + Overfit Test: {train_duration} detik")

    print_stability(config_label, stab, train_f1)
    return stab, train_f1, cv_duration, train_duration


def main():
    session_ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = os.path.join("results", f"comparison_{session_ts}")
    os.makedirs(session_dir, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  PIPELINE COMPARISON SESSION")
    print(f"  Timestamp : {session_ts}")
    print(f"  Output    : {session_dir}")
    print(f"  Configs   : {len(CONFIGS)}")
    print(f"  CV runs   : {N_RUNS}x per config")
    print(f"  Folds     : {FOLDS}")
    print(f"{'='*60}")

    all_results = []
    for config_label, config_path in CONFIGS:
        if not os.path.exists(config_path):
            print(f"\nSKIP: {config_path} tidak ditemukan.")
            continue
        stab, train_f1, cv_dur, train_dur = run_config(
            config_label, config_path, session_dir
        )
        all_results.append((config_label, stab, train_f1 or 0, cv_dur, train_dur))

    # Final comparison summary
    print(f"\n\n{'='*60}")
    print("  FINAL COMPARISON SUMMARY")
    print(f"{'='*60}")
    header_cols = ["Config", "Intent F1", "±", "Int Prec", "Int Rec", "Entity F1", "±", "Gap", "CV (s)", "Train (s)", "Verdict"]
    print(f"  {header_cols[0]:<20} {header_cols[1]:>10} {header_cols[2]:>6} {header_cols[3]:>9} {header_cols[4]:>9} {header_cols[5]:>10} {header_cols[6]:>6} {header_cols[7]:>7} {header_cols[8]:>7} {header_cols[9]:>7}  {header_cols[10]}")
    print(f"  {'-'*20} {'-'*10} {'-'*6} {'-'*9} {'-'*9} {'-'*10} {'-'*6} {'-'*7} {'-'*7} {'-'*7}  {'-'*22}")

    best_f1 = -1
    best_config = ""
    for config_label, stab, train_f1, cv_dur, train_dur in all_results:
        i_f1 = stab.get("intent_overall_mean", 0)
        i_std = stab.get("intent_overall_std", 0)
        i_prec = stab.get("intent_overall_precision_mean", 0)
        i_rec = stab.get("intent_overall_recall_mean", 0)
        e_f1 = stab.get("entity_overall_mean", 0)
        e_std = stab.get("entity_overall_std", 0)
        gap = round(train_f1 - i_f1, 4) if train_f1 else 0
        if gap > 0.15:
            verdict = "OVERFIT"
        elif gap > 0.05:
            verdict = "SEDIKIT OVERFIT"
        else:
            verdict = "GOOD FIT"

        marker = " <<" if i_f1 > best_f1 else ""
        if i_f1 > best_f1:
            best_f1 = i_f1
            best_config = config_label

        print(
            f"  {config_label:<20} {i_f1:>10.4f} {i_std:>6.4f} "
            f"{i_prec:>9.4f} {i_rec:>9.4f} "
            f"{e_f1:>10.4f} {e_std:>6.4f} {gap:>7.4f} "
            f"{cv_dur:>7.1f} {train_dur:>7.1f}  {verdict}{marker}"
        )

    print(f"\n  Config terbaik (Intent F1): {best_config} ({best_f1:.4f})")

    print(f"\n{'='*60}")
    print("  MENYIMPAN CSV...")
    print(f"{'='*60}")
    if all_results:
        save_comparison_csv(all_results, session_dir)

    print(f"\n{'='*60}")
    print(f"  Selesai. Semua hasil di: {session_dir}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()