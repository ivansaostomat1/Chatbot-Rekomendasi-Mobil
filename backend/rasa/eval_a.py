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
    ("CP_baseline", "configCP.yml"),
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
        summary["intent_overall_f1"] = data.get("weighted avg", {}).get("f1-score")
        summary["intent_overall_acc"] = data.get("accuracy")
        summary["intent_per_class"] = {
            k: round(v["f1-score"], 4)
            for k, v in data.items()
            if isinstance(v, dict)
            and "f1-score" in v
            and k not in ("macro avg", "weighted avg", "micro avg")
        }

    entity_path = os.path.join(results_dir, "DIETClassifier_report.json")
    if os.path.exists(entity_path):
        with open(entity_path, encoding="utf-8") as f:
            data = json.load(f)
        summary["entity_overall_f1"] = data.get("weighted avg", {}).get("f1-score")
        summary["entity_per_class"] = {
            k: round(v["f1-score"], 4)
            for k, v in data.items()
            if isinstance(v, dict)
            and "f1-score" in v
            and k not in ("macro avg", "weighted avg", "micro avg")
        }

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

    vals = [s["intent_overall_f1"] for s in summaries if "intent_overall_f1" in s]
    if vals:
        mean = sum(vals) / len(vals)
        if len(vals) > 1:
            variance = sum((x - mean) ** 2 for x in vals) / (len(vals) - 1)
            std = variance ** 0.5
        else:
            std = 0.0
        result["intent_overall_mean"] = round(mean, 4)
        result["intent_overall_std"] = round(std, 4)

    all_intents = set()
    for s in summaries:
        all_intents.update(s.get("intent_per_class", {}).keys())
    result["intent_per_class"] = {}
    for intent in sorted(all_intents):
        vals = [
            s["intent_per_class"][intent]
            for s in summaries
            if intent in s.get("intent_per_class", {})
        ]
        if vals:
            mean = sum(vals) / len(vals)
            if len(vals) > 1:
                variance = sum((x - mean) ** 2 for x in vals) / (len(vals) - 1)
                std = variance ** 0.5
            else:
                std = 0.0
            result["intent_per_class"][intent] = (round(mean, 4), round(std, 4))

    vals = [s["entity_overall_f1"] for s in summaries if "entity_overall_f1" in s]
    if vals:
        mean = sum(vals) / len(vals)
        if len(vals) > 1:
            variance = sum((x - mean) ** 2 for x in vals) / (len(vals) - 1)
            std = variance ** 0.5
        else:
            std = 0.0
        result["entity_overall_mean"] = round(mean, 4)
        result["entity_overall_std"] = round(std, 4)

    all_entities = set()
    for s in summaries:
        all_entities.update(s.get("entity_per_class", {}).keys())
    result["entity_per_class"] = {}
    for entity in sorted(all_entities):
        vals = [
            s["entity_per_class"][entity]
            for s in summaries
            if entity in s.get("entity_per_class", {})
        ]
        if vals:
            mean = sum(vals) / len(vals)
            if len(vals) > 1:
                variance = sum((x - mean) ** 2 for x in vals) / (len(vals) - 1)
                std = variance ** 0.5
            else:
                std = 0.0
            result["entity_per_class"][entity] = (round(mean, 4), round(std, 4))

    return result


def print_stability(label, stab, train_f1=None):
    print(f"\n{'='*60}")
    print(f"HASIL: {label}")
    print(f"{'='*60}")

    if "intent_overall_mean" in stab:
        f1 = stab["intent_overall_mean"]
        std = stab["intent_overall_std"]
        print(f"\n  [INTENT] Overall F1 : {f1:.4f} ± {std:.4f}")
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
        for intent, (mean, std) in stab.get("intent_per_class", {}).items():
            flags = []
            if mean < 0.80:
                flags.append("LEMAH")
            if std > 0.05:
                flags.append("TIDAK STABIL")
            flag_str = "  <-- " + ", ".join(flags) if flags else ""
            print(f"    {intent:<30} {mean:.4f} ± {std:.4f}{flag_str}")

    if "entity_overall_mean" in stab:
        f1 = stab["entity_overall_mean"]
        std = stab["entity_overall_std"]
        print(f"\n  [ENTITY] Overall F1 : {f1:.4f} ± {std:.4f}")
        print(f"\n  Entity per class (mean ± std):")
        for entity, (mean, std) in stab.get("entity_per_class", {}).items():
            flags = []
            if mean < 0.70:
                flags.append("LEMAH")
            if std > 0.05:
                flags.append("TIDAK STABIL")
            flag_str = "  <-- " + ", ".join(flags) if flags else ""
            print(f"    {entity:<30} {mean:.4f} ± {std:.4f}{flag_str}")


def save_comparison_csv(all_results, session_dir):
    overview_path = os.path.join(session_dir, "comparison_overview.csv")
    overview_rows = []
    for config_label, stab, train_f1, cv_dur, train_dur in all_results:
        intent_f1 = stab.get("intent_overall_mean", "")
        intent_std = stab.get("intent_overall_std", "")
        entity_f1 = stab.get("entity_overall_mean", "")
        entity_std = stab.get("entity_overall_std", "")
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
                "intent_train_f1": round(train_f1, 4) if train_f1 else "",
                "gap_train_vs_cv": gap,
                "overfit_verdict": verdict,
                "entity_f1_mean": entity_f1,
                "entity_f1_std": entity_std,
                "cv_duration_seconds": cv_dur,
                "train_duration_seconds": train_dur,
            }
        )

    fieldnames = [
        "config",
        "intent_f1_mean",
        "intent_f1_std",
        "entity_f1_mean",
        "entity_f1_std",
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

    for class_type, labels, key in [
        ("intent", sorted(all_intent_labels), "intent_per_class"),
        ("entity", sorted(all_entity_labels), "entity_per_class"),
    ]:
        for label in labels:
            row = {"type": class_type, "class": label}
            for config_label, stab, _, _, _ in all_results:
                per_class = stab.get(key, {})
                if label in per_class:
                    mean, std = per_class[label]
                    row[f"{config_label}_f1"] = mean
                    row[f"{config_label}_std"] = std
                else:
                    row[f"{config_label}_f1"] = ""
                    row[f"{config_label}_std"] = ""
            detail_rows.append(row)

    fieldnames = ["type", "class"]
    for config_label, _, _, _, _ in all_results:
        fieldnames += [f"{config_label}_f1", f"{config_label}_std"]

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
    header_cols = ["Config", "Intent F1", "±", "Entity F1", "±", "Gap", "CV (s)", "Train (s)", "Verdict"]
    print(f"  {header_cols[0]:<20} {header_cols[1]:>10} {header_cols[2]:>6} {header_cols[3]:>10} {header_cols[4]:>6} {header_cols[5]:>7} {header_cols[6]:>7} {header_cols[7]:>7}  {header_cols[8]}")
    print(f"  {'-'*20} {'-'*10} {'-'*6} {'-'*10} {'-'*6} {'-'*7} {'-'*7} {'-'*7}  {'-'*22}")

    best_f1 = -1
    best_config = ""
    for config_label, stab, train_f1, cv_dur, train_dur in all_results:
        i_f1 = stab.get("intent_overall_mean", 0)
        i_std = stab.get("intent_overall_std", 0)
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