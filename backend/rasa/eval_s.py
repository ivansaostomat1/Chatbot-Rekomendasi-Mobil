"""
evaluate_single_config.py
Menguji satu file konfigurasi pipeline (*.yml) dengan cross‑validation
dan deteksi overfit. Hasil disimpan dalam CSV yang mudah dibaca.
"""

import subprocess
import os
import datetime
import json
import csv
import sys

# ================================================================
# KONFIGURASI – ubah di sini sesuai kebutuhan
# ================================================================
# CONFIG_PATH = "configTAv6.yml"
CONFIG_PATH = "configTAv7.yml"
CONFIG_LABEL = None  # biarkan None, akan diambil dari nama file
NLU_DATA = "data/nlu.yml"
MODELS_DIR = "models"
N_CV_RUNS = 3
FOLDS = 5
# ================================================================


def run_command(command, description, log_file=None):
    print(f"\n--- {description} ---")
    print(f"Cmd: {' '.join(command)}")
    try:
        result = subprocess.run(
            command,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(result.stdout)
        tail = result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout
        print(tail)
        return True
    except subprocess.CalledProcessError as e:
        print(f"GAGAL (exit {e.returncode})")
        if e.output:
            print(e.output[-2000:])
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(e.output or "")
        return False


def extract_f1(results_dir):
    out = {
        "intent_overall": None,
        "entity_overall": None,
        "intent_per_class": {},
        "entity_per_class": {},
        "accuracy": None,
    }

    ip = os.path.join(results_dir, "intent_report.json")
    if os.path.exists(ip):
        with open(ip, encoding="utf-8") as f:
            data = json.load(f)
        out["accuracy"] = data.get("accuracy")
        wavg = data.get("weighted avg", {})
        out["intent_overall"] = wavg.get("f1-score")
        for k, v in data.items():
            if (
                isinstance(v, dict)
                and "f1-score" in v
                and k not in ("macro avg", "weighted avg", "micro avg", "accuracy")
            ):
                out["intent_per_class"][k] = round(v["f1-score"], 4)

    ep = os.path.join(results_dir, "DIETClassifier_report.json")
    if os.path.exists(ep):
        with open(ep, encoding="utf-8") as f:
            data = json.load(f)
        wavg = data.get("weighted avg", {})
        out["entity_overall"] = wavg.get("f1-score")
        for k, v in data.items():
            if (
                isinstance(v, dict)
                and "f1-score" in v
                and k not in ("macro avg", "weighted avg", "micro avg", "accuracy")
            ):
                out["entity_per_class"][k] = round(v["f1-score"], 4)

    return out


def compute_stability(cv_summaries):
    stab = {}

    # Helper untuk mean & sample std
    def mean_std(vals):
        if not vals:
            return None, None
        mean = sum(vals) / len(vals)
        if len(vals) > 1:
            var = sum((x - mean) ** 2 for x in vals) / (len(vals) - 1)
            std = var**0.5
        else:
            std = 0.0
        return round(mean, 4), round(std, 4)

    # Intent overall
    vals = [
        s["intent_overall"] for s in cv_summaries if s["intent_overall"] is not None
    ]
    mean, std = mean_std(vals)
    if mean is not None:
        stab["intent_overall_mean"] = mean
        stab["intent_overall_std"] = std

    # Entity overall
    vals = [
        s["entity_overall"] for s in cv_summaries if s["entity_overall"] is not None
    ]
    mean, std = mean_std(vals)
    if mean is not None:
        stab["entity_overall_mean"] = mean
        stab["entity_overall_std"] = std

    # Per intent
    all_intents = set()
    for s in cv_summaries:
        all_intents.update(s.get("intent_per_class", {}).keys())
    stab["intent_per_class"] = {}
    for intent in sorted(all_intents):
        vals = [
            s["intent_per_class"][intent]
            for s in cv_summaries
            if intent in s.get("intent_per_class", {})
        ]
        mean, std = mean_std(vals)
        if mean is not None:
            stab["intent_per_class"][intent] = (mean, std)

    # Per entity
    all_entities = set()
    for s in cv_summaries:
        all_entities.update(s.get("entity_per_class", {}).keys())
    stab["entity_per_class"] = {}
    for entity in sorted(all_entities):
        vals = [
            s["entity_per_class"][entity]
            for s in cv_summaries
            if entity in s.get("entity_per_class", {})
        ]
        mean, std = mean_std(vals)
        if mean is not None:
            stab["entity_per_class"][entity] = (mean, std)

    return stab


def print_evaluation(label, stab, train_f1):
    print(f"\n{'='*60}")
    print(f"HASIL EVALUASI: {label}")
    print(f"{'='*60}")

    if "intent_overall_mean" in stab:
        f1 = stab["intent_overall_mean"]
        std = stab["intent_overall_std"]
        print(f"\n[INTENT] Overall F1 : {f1:.4f} ± {std:.4f}")
        if train_f1 is not None:
            gap = round(train_f1 - f1, 4)
            if gap > 0.15:
                v = "OVERFIT"
            elif gap > 0.05:
                v = "SEDIKIT OVERFIT (wajar)"
            else:
                v = "GENERALISASI BAIK"
            print(f"         Training F1 : {train_f1:.4f}  →  Gap: {gap:.4f}  →  {v}")

        print("\nIntent per class (mean ± std):")
        for intent, (mean, std) in stab.get("intent_per_class", {}).items():
            flags = []
            if mean < 0.80:
                flags.append("LEMAH")
            if std > 0.05:
                flags.append("TIDAK STABIL")
            flag_str = "  <-- " + ", ".join(flags) if flags else ""
            print(f"  {intent:<30} {mean:.4f} ± {std:.4f}{flag_str}")

    if "entity_overall_mean" in stab:
        f1 = stab["entity_overall_mean"]
        std = stab["entity_overall_std"]
        print(f"\n[ENTITY] Overall F1 : {f1:.4f} ± {std:.4f}")

        print("\nEntity per class (mean ± std):")
        for entity, (mean, std) in stab.get("entity_per_class", {}).items():
            flags = []
            if mean < 0.70:
                flags.append("LEMAH")
            if std > 0.05:
                flags.append("TIDAK STABIL")
            flag_str = "  <-- " + ", ".join(flags) if flags else ""
            print(f"  {entity:<30} {mean:.4f} ± {std:.4f}{flag_str}")


def save_csv(session_dir, label, stab, train_f1, cv_summaries, tt_summary):
    # Ringkasan overall
    overview_path = os.path.join(session_dir, "ringkasan_overall.csv")
    with open(overview_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "Nama Konfigurasi",
                "Intent F1 (CV Mean)",
                "Intent F1 (CV Std)",
                "Entity F1 (CV Mean)",
                "Entity F1 (CV Std)",
                "Intent F1 (Training)",
                "Selisih Intent (Training - CV)",
                "Status Overfit",
            ]
        )
        intent_cv = stab.get("intent_overall_mean", "")
        intent_std = stab.get("intent_overall_std", "")
        entity_cv = stab.get("entity_overall_mean", "")
        entity_std = stab.get("entity_overall_std", "")
        gap = (
            round(train_f1 - intent_cv, 4)
            if (train_f1 is not None and intent_cv != "")
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
            verdict = ""
        writer.writerow(
            [
                label,
                intent_cv,
                intent_std,
                entity_cv,
                entity_std,
                round(train_f1, 4) if train_f1 else "",
                gap,
                verdict,
            ]
        )
    print(f"CSV ringkasan disimpan: {overview_path}")

    # Detail per kelas
    detail_path = os.path.join(session_dir, "detail_per_kelas.csv")
    with open(detail_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "Tipe",
                "Nama Kelas",
                "F1 CV (Mean)",
                "F1 CV (Std)",
                "F1 Training (sendiri)",
            ]
        )

        for intent, (mean, std) in stab.get("intent_per_class", {}).items():
            train_val = (
                tt_summary.get("intent_per_class", {}).get(intent, "")
                if tt_summary
                else ""
            )
            writer.writerow(["intent", intent, mean, std, train_val])

        for entity, (mean, std) in stab.get("entity_per_class", {}).items():
            train_val = (
                tt_summary.get("entity_per_class", {}).get(entity, "")
                if tt_summary
                else ""
            )
            writer.writerow(["entity", entity, mean, std, train_val])

    print(f"CSV detail per kelas disimpan: {detail_path}")


def main():
    if not os.path.exists(CONFIG_PATH):
        print(f"ERROR: File config tidak ditemukan: {CONFIG_PATH}")
        sys.exit(1)

    global CONFIG_LABEL
    if CONFIG_LABEL is None:
        CONFIG_LABEL = os.path.splitext(os.path.basename(CONFIG_PATH))[0]

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = os.path.join("results", f"single_{CONFIG_LABEL}_{timestamp}")
    os.makedirs(session_dir, exist_ok=True)

    print(f"\n{'#'*60}")
    print(f"EVALUASI KONFIGURASI TUNGGAL")
    print(f"Config : {CONFIG_PATH}")
    print(f"Label  : {CONFIG_LABEL}")
    print(f"Folder : {session_dir}")
    print(f"{'#'*60}")

    # Cross-Validation
    cv_summaries = []
    for run_idx in range(1, N_CV_RUNS + 1):
        cv_dir = os.path.join(session_dir, f"cv_run_{run_idx}")
        os.makedirs(cv_dir, exist_ok=True)
        print(f"\n[CV Run {run_idx}/{N_CV_RUNS}]")
        ok = run_command(
            [
                "rasa",
                "test",
                "nlu",
                "--nlu",
                NLU_DATA,
                "--config",
                CONFIG_PATH,
                "--cross-validation",
                "--folds",
                str(FOLDS),
                "--out",
                cv_dir,
            ],
            f"Cross-Validation run {run_idx}",
            log_file=os.path.join(cv_dir, "log.txt"),
        )
        if ok:
            summary = extract_f1(cv_dir)
            cv_summaries.append(summary)
        else:
            print(f"CV run {run_idx} gagal, dilanjutkan.")

    if not cv_summaries:
        print("Tidak ada CV yang berhasil. Keluar.")
        sys.exit(1)

    stab = compute_stability(cv_summaries)

    # Training + Overfit Detection
    print(f"\n[TRAINING] Melatih model dengan config {CONFIG_LABEL}")
    train_ok = run_command(
        ["rasa", "train", "nlu", "--config", CONFIG_PATH],
        f"Training NLU {CONFIG_LABEL}",
        log_file=os.path.join(session_dir, "train_output.log"),
    )

    train_f1 = None
    tt_summary = None
    if train_ok:
        model_files = [
            f
            for f in os.listdir(MODELS_DIR)
            if f.startswith("nlu-") and f.endswith(".tar.gz")
        ]
        if model_files:
            # Gunakan model dengan waktu modifikasi terbaru
            latest_model = max(
                [os.path.join(MODELS_DIR, f) for f in model_files],
                key=os.path.getmtime,
            )
            tt_dir = os.path.join(session_dir, "train_test")
            os.makedirs(tt_dir, exist_ok=True)
            tt_ok = run_command(
                [
                    "rasa",
                    "test",
                    "nlu",
                    "--nlu",
                    NLU_DATA,
                    "--model",
                    latest_model,
                    "--out",
                    tt_dir,
                ],
                "Overfit Detection (Test pada training data)",
                log_file=os.path.join(tt_dir, "log.txt"),
            )
            if tt_ok:
                tt_summary = extract_f1(tt_dir)
                train_f1 = tt_summary.get("intent_overall")
        else:
            print("Model tidak ditemukan setelah training.")
    else:
        print("Training gagal, overfit detection tidak dapat dilakukan.")

    print_evaluation(CONFIG_LABEL, stab, train_f1)
    save_csv(session_dir, CONFIG_LABEL, stab, train_f1, cv_summaries, tt_summary)

    print(f"\nSemua hasil tersimpan di: {session_dir}\n")


if __name__ == "__main__":
    main()
