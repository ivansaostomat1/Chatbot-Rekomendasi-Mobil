"""
check_overfit.py
Mengecek tingkat overfit semua konfigurasi pipeline.
Menjalankan 1× cross-validation (CV) dan training+test pada data training,
lalu menghitung selisih (gap) F1 intent. Gap besar → overfit.
Hasil disimpan ke CSV.
"""

import subprocess
import os
import datetime
import json
import csv
import sys
import time

# ================================================================
# KONFIGURASI
# ================================================================
NLU_DATA = "data/nlu.yml"
MODELS_DIR = "models"
FOLDS = 5  # fold untuk CV
N_CV_RUNS = 1  # cukup 1× CV agar cepat

CONFIGS = [
    ("Default", "configDefault.yml"),
    ("TAv1_sparse", "configTAv1.yml"),
    ("TAv2_indobert", "configTAv2.yml"),
    ("TAv3_hybrid", "configTAv3.yml"),
    ("TAv4_deep", "configTAv4.yml"),
    ("TAv5_large", "configTAv5.yml"),
]
# ================================================================


def run_cmd(cmd, desc, log_file=None):
    print(f"\n--- {desc} ---")
    try:
        proc = subprocess.run(
            cmd, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        if log_file:
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(proc.stdout)
        tail = proc.stdout[-2000:] if len(proc.stdout) > 2000 else proc.stdout
        print(tail)
        return True
    except subprocess.CalledProcessError as e:
        print(f"GAGAL (exit {e.returncode})")
        if e.output:
            print(e.output[-2000:])
        if log_file:
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(e.output or "")
        return False


def get_intent_f1(results_dir):
    """Ambil weighted avg F1 intent dari intent_report.json."""
    ip = os.path.join(results_dir, "intent_report.json")
    if os.path.exists(ip):
        with open(ip, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("weighted avg", {}).get("f1-score")
    return None


def main():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join("results", f"overfit_check_{timestamp}")
    os.makedirs(out_dir, exist_ok=True)

    rows = []

    for label, cfg_path in CONFIGS:
        if not os.path.exists(cfg_path):
            print(f"SKIP: {cfg_path} tidak ada.")
            continue

        print(f"\n{'#'*50}\n>>> CONFIG: {label}\n{'#'*50}")

        # 1. Cross-validation (1 run)
        cv_dir = os.path.join(out_dir, f"{label}_cv")
        os.makedirs(cv_dir, exist_ok=True)
        cv_start = time.time()
        cv_ok = run_cmd(
            [
                "rasa",
                "test",
                "nlu",
                "--nlu",
                NLU_DATA,
                "--config",
                cfg_path,
                "--cross-validation",
                "--folds",
                str(FOLDS),
                "--out",
                cv_dir,
            ],
            f"{label} CV",
            log_file=os.path.join(cv_dir, "log.txt"),
        )
        cv_dur = round(time.time() - cv_start, 2)
        cv_f1 = get_intent_f1(cv_dir) if cv_ok else None

        # 2. Training + test pada data training (overfit test)
        train_dir = os.path.join(out_dir, f"{label}_model")
        os.makedirs(train_dir, exist_ok=True)
        train_start = time.time()
        train_ok = run_cmd(
            ["rasa", "train", "nlu", "--config", cfg_path, "--out", train_dir],
            f"{label} Training",
            log_file=os.path.join(train_dir, "train_log.txt"),
        )

        train_f1 = None
        if train_ok:
            # cari model terbaru di train_dir
            model_tgz = None
            for f in os.listdir(train_dir):
                if f.endswith(".tar.gz"):
                    model_tgz = os.path.join(train_dir, f)
                    break
            if model_tgz:
                tt_dir = os.path.join(out_dir, f"{label}_train_test")
                os.makedirs(tt_dir, exist_ok=True)
                tt_ok = run_cmd(
                    [
                        "rasa",
                        "test",
                        "nlu",
                        "--nlu",
                        NLU_DATA,
                        "--model",
                        model_tgz,
                        "--out",
                        tt_dir,
                    ],
                    f"{label} Train-Test",
                    log_file=os.path.join(tt_dir, "log.txt"),
                )
                if tt_ok:
                    train_f1 = get_intent_f1(tt_dir)
        train_dur = round(time.time() - train_start, 2)

        # 3. Hitung gap
        gap = (
            round(train_f1 - cv_f1, 4)
            if (cv_f1 is not None and train_f1 is not None)
            else ""
        )
        if gap != "":
            # Tambahkan pengecekan Underfit di sini
            if train_f1 < 0.80:
                verdict = "UNDERFIT (Skor F1 terlalu rendah)"
            elif gap > 0.15:
                verdict = "OVERFIT"
            elif gap > 0.05:
                verdict = "SEDIKIT OVERFIT"
            else:
                verdict = "GENERALISASI BAIK"
        else:
            verdict = "GAGAL EVALUASI"

        print(f"\n  Intent CV F1 : {cv_f1}")
        print(f"  Intent Train F1 : {train_f1}")
        print(f"  Gap (Train - CV) : {gap}  →  {verdict}")
        print(f"  Durasi CV : {cv_dur} detik")
        print(f"  Durasi Train+Test : {train_dur} detik")

        rows.append(
            {
                "config": label,
                "intent_cv_f1": cv_f1 if cv_f1 is not None else "N/A",
                "intent_train_f1": train_f1 if train_f1 is not None else "N/A",
                "gap": gap,
                "overfit_verdict": verdict,
                "cv_duration_seconds": cv_dur,
                "train_duration_seconds": train_dur,
            }
        )

    # 4. Simpan CSV ringkasan
    csv_path = os.path.join(out_dir, "overfit_summary.csv")
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "config",
                "intent_cv_f1",
                "intent_train_f1",
                "gap",
                "overfit_verdict",
                "cv_duration_seconds",
                "train_duration_seconds",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    # 5. Tampilkan tabel akhir
    print(f"\n{'='*80}")
    print("RINGKASAN OVERFIT / UNDERFIT")
    print(f"{'='*80}")
    print(
        f"{'Config':<20} {'CV F1':>8} {'Train F1':>9} {'Gap':>8} {'Verdict':>20} {'CV(s)':>7} {'Train(s)':>8}"
    )
    print("-" * 80)
    for r in rows:
        print(
            f"{r['config']:<20} {str(r['intent_cv_f1']):>8} {str(r['intent_train_f1']):>9} "
            f"{str(r['gap']):>8} {r['overfit_verdict']:<20} {str(r['cv_duration_seconds']):>7} {str(r['train_duration_seconds']):>8}"
        )

    print(f"\nCSV disimpan → {csv_path}")
    print(f"Detail ada di folder: {out_dir}")


if __name__ == "__main__":
    main()
