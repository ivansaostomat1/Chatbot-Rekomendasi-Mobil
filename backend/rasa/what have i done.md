
# Konteks Penelitian: Optimasi Pipeline Rasa NLU

Dokumen ini merupakan kompilasi dari seluruh konfigurasi, skrip eksekusi eksperimen, alat ekstraksi, serta data hasil pengujian yang dilakukan dalam proses optimasi pipeline Rasa NLU.

Dokumen ini tidak memuat klaim atau teori baru, melainkan hanya menjabarkan **apa yang telah dilakukan** di dalam kode dan **apa hasil dari metrik pengujian** yang didapat, sehingga dapat menjadi acuan (konteks) yang akurat.

---

## 1. File Konfigurasi Eksperimen

**File:** `config untuk eksperimen.txt`
**Kegunaan di Penelitian:**
File ini berisi seluruh resep konfigurasi pipeline NLU yang diujikan dalam penelitian ini. Terdapat beberapa variasi (TAv1 hingga TAv6) yang masing-masing memiliki fokus modifikasi komponen, seperti penyesuaian parameter `DIETClassifier`, penggunaan model bahasa IndoBERT (`LanguageModelFeaturizer`), pengaturan fitur `CountVectorsFeaturizer`, hingga penggunaan `RegexEntityExtractor`. Tujuannya adalah mencari kombinasi pipeline yang optimal untuk memahami _intent_ dan menangkap _entity_ (terutama entitas negasi) dalam bahasa Indonesia.

```yaml
==================================================
 SECTION: configCP.yml (Baseline)
==================================================

# The config recipe.
recipe: default.v1
language: id

pipeline:
# # No configuration for the NLU pipeline was provided. The following default pipeline was used to train your model.
#   - name: WhitespaceTokenizer
#   - name: RegexFeaturizer
#   - name: LexicalSyntacticFeaturizer
#   - name: CountVectorsFeaturizer
#   - name: CountVectorsFeaturizer
#     analyzer: char_wb
#     min_ngram: 1
#     max_ngram: 4
#   - name: DIETClassifier
#     epochs: 100
#     constrain_similarities: true
#   - name: EntitySynonymMapper
#   - name: ResponseSelector
#     epochs: 100
#     constrain_similarities: true
#   - name: FallbackClassifier
#     threshold: 0.3
#     ambiguity_threshold: 0.1

policies:
#   - name: MemoizationPolicy
#   - name: RulePolicy
#   - name: UnexpecTEDIntentPolicy
#     max_history: 5
#     epochs: 100
#   - name: TEDPolicy
#     max_history: 5
#     epochs: 100
#     constrain_similarities: true

==================================================
 SECTION: configTAv1.yml 
==================================================

recipe: default.v1
language: id

# TAv1 — Hyperparameter Tuning Only
# Fokus: optimasi angka DIET tanpa ubah komponen pipeline
# Perubahan dari versi lama:
#   - epochs DIETClassifier: 75 → 150 (lebih konvergen)
#   - learning_rate: eksplisit 0.001 (stabil)
#   - char_wb max_ngram: 4 → 3 (kurangi noise overlap negasi)
#   - batch_size: [64, 256] (curriculum batching)

pipeline:
  - name: WhitespaceTokenizer
  - name: RegexFeaturizer
  - name: LexicalSyntacticFeaturizer
  - name: CountVectorsFeaturizer
  - name: CountVectorsFeaturizer
    analyzer: char_wb
    min_ngram: 1
    max_ngram: 3
  - name: DIETClassifier
    epochs: 150
    learning_rate: 0.001
    batch_size: [64, 256]
    constrain_similarities: true
    entity_recognition: true
  - name: EntitySynonymMapper
  - name: ResponseSelector
    epochs: 100
    constrain_similarities: true

policies:
  - name: MemoizationPolicy
  - name: RulePolicy

==================================================
 SECTION: configTAv2.yml 
==================================================

recipe: default.v1
language: id

# TAv2 — IndoBERT (HuggingFace Transformers) Only
# Fokus: ganti seluruh featurizer ke pre-trained IndoBERT
# Model: indobenchmark/indobert-base-p1
# Perubahan dari versi lama:
#   - Hapus CountVectorsFeaturizer (digantikan LanguageModelFeaturizer)
#   - Hapus LexicalSyntacticFeaturizer
#   - Tambah HFTransformersNLP + LanguageModelTokenizer + LanguageModelFeaturizer
#   - epochs diturunkan ke 50 (embeddings sudah kuat, tidak perlu banyak epoch)
#   - Tetap pakai RegexFeaturizer untuk pattern budget/angka

pipeline:
  - name: WhitespaceTokenizer
    intent_tokenization_flag: false
    intent_split_symbol: "_"
  - name: LanguageModelFeaturizer
    model_name: "bert"
    model_weights: "indobenchmark/indobert-base-p1"
  - name: RegexFeaturizer
  - name: DIETClassifier
    epochs: 50
    learning_rate: 0.001
    constrain_similarities: true
    entity_recognition: true
  - name: EntitySynonymMapper
  - name: ResponseSelector
    epochs: 50
    constrain_similarities: true

policies:
  - name: MemoizationPolicy
  - name: RulePolicy

==================================================
 SECTION: configTAv3.yml 
==================================================

recipe: default.v1
language: id

# TAv3 — Gabungan CountVectors + RegexEntityExtractor + LexicalSyntactic
# Fokus: perkuat deteksi negasi dengan rule-based tanpa Spacy
# Perubahan dari versi lama:
#   - Tambah RegexEntityExtractor (tangkap pola negasi eksplisit rule-based)
#   - Tambah LexicalSyntacticFeaturizer lebih dalam (prefix/suffix awareness)
#   - char_wb max_ngram dipersempit ke 3 (kurangi noise overlap negasi)
#   - epochs 100, dropout 0.2, learning_rate eksplisit

pipeline:
  - name: WhitespaceTokenizer
  - name: RegexFeaturizer
  - name: LexicalSyntacticFeaturizer
  - name: CountVectorsFeaturizer
  - name: CountVectorsFeaturizer
    analyzer: char_wb
    min_ngram: 1
    max_ngram: 3
  - name: DIETClassifier
    epochs: 100
    learning_rate: 0.001
    dropout_rate: 0.2
    constrain_similarities: true
    entity_recognition: true
  - name: EntitySynonymMapper
  - name: RegexEntityExtractor
    use_lookup_tables: true
    use_regexes: true
    use_word_boundaries: true
  - name: ResponseSelector
    epochs: 100
    constrain_similarities: true

policies:
  - name: MemoizationPolicy
  - name: RulePolicy

==================================================
 SECTION: configTAv4.yml 
==================================================

recipe: default.v1
language: id

# TAv4 — IndoBERT + RegexEntityExtractor (Kandidat Terbaik Sebelumnya)
# Fokus: kontekstual semantik (IndoBERT) + rule-based fallback (Regex)
# Strategi: IndoBERT tangkap semantik kompleks, Regex tangkap pola negasi eksplisit

pipeline:
  - name: WhitespaceTokenizer
    intent_tokenization_flag: false
    intent_split_symbol: "_"
  - name: LanguageModelFeaturizer
    model_name: "bert"
    model_weights: "indobenchmark/indobert-base-p1"
  - name: RegexFeaturizer
  - name: DIETClassifier
    epochs: 75
    learning_rate: 0.001
    batch_size: [64, 256]
    constrain_similarities: true
    entity_recognition: true
  - name: EntitySynonymMapper
  - name: RegexEntityExtractor
    use_lookup_tables: true
    use_regexes: true
    use_word_boundaries: true
  - name: FallbackClassifier
    threshold: 0.6
    ambiguity_threshold: 0.1
  - name: ResponseSelector
    epochs: 75
    constrain_similarities: true

policies:
  - name: MemoizationPolicy
  - name: RulePolicy

==================================================
 SECTION: configTAv5.yml 
==================================================

recipe: default.v1
language: id

# TAv5 — IndoBERT + RegexEntityExtractor + Regularization
# Fokus: Mencegah overfitting dari TAv4 dengan menambahkan dropout_rate: 0.2 pada DIETClassifier.
# Hasil: Berhasil mencapai generalisasi sangat baik (gap latih-uji negatif), namun kemampuannya menangkap entitas negasi kompleks (seperti feature.negated) justru menurun signifikan.

pipeline:
  - name: WhitespaceTokenizer
    intent_tokenization_flag: false
    intent_split_symbol: "_"
  - name: LanguageModelFeaturizer
    model_name: "bert"
    model_weights: "indobenchmark/indobert-base-p1"
  - name: RegexFeaturizer
  - name: DIETClassifier
    epochs: 75
    learning_rate: 0.001
    batch_size: [64, 256]
    dropout_rate: 0.2
    constrain_similarities: true
    entity_recognition: true
  - name: EntitySynonymMapper
  - name: RegexEntityExtractor
    use_lookup_tables: true
    use_regexes: true
    use_word_boundaries: true
  - name: FallbackClassifier
    threshold: 0.4
    ambiguity_threshold: 0.1
  - name: ResponseSelector
    epochs: 75
    constrain_similarities: true

policies:
  - name: MemoizationPolicy
  - name: RulePolicy

==================================================
 SECTION: configTAv6.yml 
==================================================

recipe: default.v1
language: id

# TAv6 — Most Optimal Performance: Ekstensif Featurizer (IndoBERT + N-Gram)
# Fokus: Menggabungkan kekuatan semantik IndoBERT dengan sensitivitas n-gram/imbuhan dari CountVectors dan LexicalSyntacticFeaturizer, dipadu dengan epochs 150.
# Hasil: Memberikan performa mutlak tertinggi (Intent F1 90.44%, Entity F1 92.06%) serta jauh lebih tangguh dalam menangkap feature.negated (81.40%) dibandingkan TAv4 dan TAv5. Meskipun sedikit overfit, ini merupakan konfigurasi paling optimal secara keseluruhan.

pipeline:
  - name: WhitespaceTokenizer
    intent_tokenization_flag: false
    intent_split_symbol: "_"
  - name: LanguageModelFeaturizer
    model_name: "bert"
    model_weights: "indobenchmark/indobert-base-p1"
  - name: RegexFeaturizer
  - name: LexicalSyntacticFeaturizer
  - name: CountVectorsFeaturizer
  - name: CountVectorsFeaturizer
    analyzer: char_wb
    min_ngram: 1
    max_ngram: 3
  - name: DIETClassifier
    epochs: 150
    learning_rate: 0.001
    batch_size: [64, 256]
    constrain_similarities: true
    entity_recognition: true
  - name: EntitySynonymMapper
  - name: FallbackClassifier
    threshold: 0.4
    ambiguity_threshold: 0.1
  - name: ResponseSelector
    epochs: 150
    constrain_similarities: true

policies:
  - name: MemoizationPolicy
  - name: RulePolicy
```

---

## 2. Skrip Pengujian Silang (Cross-Validation) & Deteksi Overfit

**File:** `eval_a.py`, `eval_s.py`, dan `check_overfit.py`
**Kegunaan di Penelitian:**
Skrip otomatisasi untuk menjalankan proses _Cross-Validation_ (evaluasi data lipat-silang) secara konsisten dan transparan. Skrip `eval_a.py` menguji seluruh daftar file konfigurasi (CP, TAv1-TAv6) secara bergantian dengan 3 putaran (run), sementara `eval_s.py` khusus untuk satu konfigurasi saja. Selain itu, terdapat skrip pendukung `check_overfit.py` yang berfungsi khusus untuk memonitor dengan cepat tingkat *overfit/underfit* seluruh konfigurasi menggunakan 1 kali putaran CV saja lalu mencetak ringkasan hasilnya. Ketiga skrip ini melakukan tugas penting berupa:

1. Menjalankan Cross-Validation (K-Fold = 5).
2. Mengeksekusi pelatihan ulang (training) menggunakan seluruh dataset.
3. Melakukan tes model yang dilatih pada data training itu sendiri (Overfit Detection) untuk mengetahui seberapa besar perbedaan (gap) _F1-Score_ antara data latih dan data uji silang.

```python
# Potongan kode utama dari eval_a.py (untuk gambaran arsitektur eksperimen)
import subprocess, os, datetime, json, csv, sys, time, glob

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

def run_config(config_label, config_path, session_dir):
    config_dir = os.path.join(session_dir, config_label)
    os.makedirs(config_dir, exist_ok=True)

    # ---------- CROSS VALIDATION ----------
    cv_summaries = []
    for run_idx in range(1, N_RUNS + 1):
        cv_dir = os.path.join(config_dir, f"cv_run{run_idx}")
        # Command: rasa test nlu --nlu data/nlu.yml --config config.yml --cross-validation --folds 5 ...
        # (kode disederhanakan)
        cv_summaries.append(extract_f1_summary(cv_dir))
  
    # ---------- TRAINING + OVERFIT DETECTION ----------
    # Command: rasa train nlu --config config.yml ...
    # Command: rasa test nlu --nlu data/nlu.yml --model latest_model ...
    # (menguji model baru pada data nlu.yml untuk mengecek overfitting)
  
    return stab, train_f1, cv_duration, train_duration
```

---

## 3. Ekstraksi dan Kompilasi Metrik

**File:** `ekstrak.py`
**Kegunaan di Penelitian:**
Mengekstrak hasil metrik _F1-score_ yang tersebar di ratusan file JSON (seperti `intent_report.json` dan `DIETClassifier_report.json`) yang dihasilkan oleh Rasa. Skrip ini menghitung nilai rata-rata (_mean_) dan standar deviasi sampel dari seluruh pengulangan _Cross-Validation_, serta membuat dua file format CSV (`perbandingan.csv` dan `detail perbandingan.csv`) yang merangkum keseluruhan performa masing-masing model untuk _Intent_ dan _Entity_.

```python
# Potongan kode utama dari ekstrak.py
import os, json, csv, glob
from statistics import mean, stdev

RESULTS_DIR = "results/comparison_20260512_145550"
OUTPUT_CSV = "perbandingan.csv"

def extract_full_metrics(results_dir):
    # Membaca metrik dari intent_report.json dan DIETClassifier_report.json
    # Mengekstrak weighted avg f1-score dan f1-score per-kelas
    pass

def compute_sample_stability(f1_values):
    # Menghitung Rata-rata F1 dan Standar Deviasi
    avg = mean(f1_values)
    std = stdev(f1_values) if len(f1_values) > 1 else 0.0
    return round(avg, 4), round(std, 4)

def main():
    # Menelusuri semua folder konfigurasi dan cv_run
    # Menyatukan metrik-metrik, membandingkan f1-score cv vs f1-score train (overfit)
    # Menulis ke file perbandingan.csv (overall) dan detail perbandingan.csv (per kelas)
    pass
```

---

## 4. Pembuatan Visualisasi Data Evaluasi

**File:** `generate_plots.py`
**Kegunaan di Penelitian:**
Mengolah data agregat dari CSV hasil ekstraksi (`perbandingan.csv` dan `detail perbandingan.csv`) ke dalam bentuk bagan untuk analisis Bab 4 penelitian. Visualisasi ini (bar chart, line chart, scatter plot, radar chart, dan confusion matrix) mempermudah identifikasi kualitatif konfigurasi mana yang paling andal, konsisten, dan memiliki generalisasi tinggi tanpa terjadinya _overfit_ yang ekstrem.

```python
# Potongan kode utama dari generate_plots.py
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

RESULTS_DIR = r"results\comparison_20260512_145550"
OUTPUT_DIR = r"gambar bab 4"
df_summary = pd.read_csv(os.path.join(RESULTS_DIR, "perbandingan.csv"))
df_detail = pd.read_csv(os.path.join(RESULTS_DIR, "detail perbandingan.csv"))

# Menghasilkan 9 gambar untuk Bab 4:
# Gambar 4.1: Bar chart — Perbandingan Intent F1-Score Antar Konfigurasi (+ Std Dev error bars)
# Gambar 4.2: Bar chart — Perbandingan Entity F1-Score Antar Konfigurasi (+ Std Dev error bars)
# Gambar 4.3: Bar chart — Perbandingan F1-Score Entitas feature.negated
# Gambar 4.4: Line chart — Stabilitas Model (Standar Deviasi Intent dan Entity)
# Gambar 4.5: Line plot — Overfitting Gap (Train F1 - CV F1)
# Gambar 4.6: Scatter plot — Trade-off Generalisasi (Gap) vs Performa (Entity F1)
# Gambar 4.7: Radar chart — Komparatif 3 Konfigurasi Terbaik (TAv4, TAv5, TAv6) [Normalized]
# Gambar 4.8: Heatmap Confusion Matrix Intent TAv5 (dari cv_run1)
# Gambar 4.9: Heatmap Confusion Matrix Intent TAv6 (dari cv_run1)
```

---

## 5. Hasil Pengujian / Data Hasil Eksperimen

**Folder:** `results/comparison_20260512_145550`
**Kegunaan di Penelitian:**
Ini adalah hasil nyata (empiris) dari komputasi evaluasi. Data dalam bentuk CSV di bawah ini merupakan metrik perbandingan performa masing-masing dari tujuh konfigurasi yang diuji.

### File 1: `perbandingan.csv` (Ikhtisar Performa Secara Keseluruhan)

Berisi Rata-Rata _F1-Score_ dan Standar Deviasi (stabilitas) untuk Intent dan Entity dari 3 kali _Cross-Validation_. Juga terdapat nilai perbandingan dengan evaluasi data _Training_ untuk mendeteksi seberapa parah gap _Overfitting_-nya.

```csv
config,intent_f1_mean,intent_f1_std,entity_f1_mean,entity_f1_std,train_intent_f1,gap(train-cv),status_overfit,num_cv_runs
CP_baseline,0.8748,0.006,0.8972,0.0007,0.9823,0.1075,SEDIKIT OVERFIT,3
TAv1,0.8758,0.0037,0.9028,0.0071,0.9537,0.0779,SEDIKIT OVERFIT,3
TAv2,0.8919,0.0071,0.8902,0.0047,0.855,-0.0369,GENERALISASI BAIK,3
TAv3,0.8791,0.0037,0.896,0.0136,0.9929,0.1138,SEDIKIT OVERFIT,3
TAv4,0.8941,0.0116,0.9018,0.0031,0.9282,0.0341,GENERALISASI BAIK,3
TAv5,0.8998,0.0041,0.9031,0.0024,0.8867,-0.0131,GENERALISASI BAIK,3
TAv6,0.9044,0.0048,0.9206,0.0039,0.9787,0.0743,SEDIKIT OVERFIT,3
```

### File 2: `detail perbandingan.csv` (Performa Per Kelas / Label)

Memperlihatkan performa _F1-score_ rata-rata di level yang lebih mikroskopis (per spesifik intent dan entitas). Hal ini krusial untuk mengamati misalnya peningkatan performa entitas negasi (`body_type.negated`, `feature.negated`, dsb).

```csv
type,class,CP_baseline_f1,CP_baseline_std,TAv1_f1,TAv1_std,TAv2_f1,TAv2_std,TAv3_f1,TAv3_std,TAv4_f1,TAv4_std,TAv5_f1,TAv5_std,TAv6_f1,TAv6_std
intent,ask_comparison,0.8825,0.013,0.8738,0.0074,0.8777,0.0253,0.882,0.0091,0.9049,0.0741,0.8843,0.0051,0.9041,0.0474
intent,ask_recommendation,0.8602,0.0069,0.8614,0.0071,0.8793,0.0089,0.8644,0.0078,0.8843,0.0085,0.8818,0.0035,0.8811,0.0131
intent,ask_similar_car,0.7522,0.0944,0.7551,0.0306,0.6797,0.0647,0.7703,0.0573,0.5966,0.1769,0.6523,0.0657,0.7905,0.0447
intent,choose_preference,0.8633,0.0106,0.8719,0.0074,0.8889,0.0018,0.8758,0.01,0.8877,0.0047,0.8941,0.0095,0.8905,0.0079
intent,out_of_scope,0.8733,0.0073,0.8625,0.0163,0.9125,0.0226,0.8704,0.0128,0.9189,0.0038,0.9424,0.0057,0.9432,0.0067
intent,start_search,0.957,0.0061,0.9517,0.016,0.9525,0.0061,0.9475,0.0094,0.9593,0.0069,0.9687,0.0021,0.9822,0.0085
entity,body_type,0.971,0.0069,0.9751,0.0122,0.9312,0.0182,0.9617,0.0128,0.9268,0.0018,0.9345,0.0066,0.9426,0.0075
entity,body_type.negated,0.9841,0.0275,0.9274,0.0255,0.7029,0.0764,0.901,0.0272,0.7803,0.0757,0.8767,0.0896,0.8857,0.0247
entity,brand,0.9184,0.0113,0.9142,0.0152,0.8905,0.0165,0.8963,0.0132,0.8779,0.0089,0.9048,0.0042,0.9162,0.0091
entity,brand.negated,0.9002,0.0163,0.8911,0.021,0.8226,0.0183,0.8601,0.0161,0.8188,0.0124,0.8283,0.0175,0.8537,0.0339
entity,budget,0.9475,0.0039,0.9403,0.0106,0.9725,0.0024,0.9391,0.0135,0.9678,0.004,0.9666,0.0027,0.9729,0.0045
entity,feature,0.9544,0.0106,0.9467,0.013,0.9577,0.0049,0.9536,0.0088,0.9621,0.0064,0.9591,0.009,0.9733,0.0078
entity,feature.negated,0.7018,0.1215,0.7725,0.0092,0.5405,0.0446,0.7168,0.0564,0.6104,0.1751,0.5417,0.0722,0.814,0.1029
entity,hard_filter,0.9838,0.0053,0.9873,0.0031,0.9836,0.0056,0.9821,0.0122,0.9891,0.0,0.9873,0.0032,0.9872,0.0063
entity,min_seat,0.8169,0.0225,0.8433,0.0356,0.9786,0.007,0.8469,0.0229,0.9856,0.0072,0.9736,0.0083,0.9787,0.0068
entity,powertrain,0.9193,0.0097,0.9402,0.0039,0.878,0.0188,0.9393,0.0147,0.9152,0.0041,0.9022,0.0224,0.9321,0.0107
entity,powertrain.negated,0.9232,0.0069,0.9354,0.0021,0.839,0.0376,0.915,0.0469,0.8776,0.0264,0.8764,0.0349,0.9245,0.0316
entity,preference,0.7932,0.0119,0.8096,0.0109,0.7798,0.007,0.7994,0.023,0.8099,0.0281,0.8009,0.004,0.8171,0.0165
entity,preference.negated,0.92,0.0181,0.9536,0.0182,0.9728,0.0139,0.9257,0.0301,0.9643,0.0277,0.978,0.02,0.9735,0.0133
entity,target_car,0.6661,0.0457,0.7541,0.0246,0.5872,0.1,0.7641,0.0154,0.66,0.0383,0.6538,0.0282,0.7238,0.1044
entity,transmission,0.949,0.0083,0.912,0.0475,0.8469,0.0299,0.9075,0.052,0.8444,0.0242,0.8936,0.0239,0.9375,0.016
entity,transmission.negated,0.9317,0.0101,0.9079,0.0645,0.8346,0.0208,0.9056,0.0511,0.8524,0.0363,0.8893,0.0357,0.9259,0.0183
```

---

## 6. Statistik Dataset (Ground Truth dari `data/nlu.yml`)

**PENTING:** Angka-angka di bawah ini dihitung langsung dari file `data/nlu.yml` yang digunakan saat eksperimen. Angka-angka ini adalah sumber kebenaran (_ground truth_) yang harus menjadi rujukan utama jika terjadi inkonsistensi dengan dokumen lain.

### 6.1 Distribusi Intent (6 intent, 850 kalimat total)

| Intent | Jumlah Sampel | Deskripsi |
|---|---|---|
| ask_recommendation | 297 | Meminta rekomendasi mobil |
| choose_preference | 282 | Menyatakan preferensi (suka/tidak suka) |
| start_search | 121 | Memulai pencarian mobil / reset |
| out_of_scope | 97 | Pertanyaan di luar domain rekomendasi mobil |
| ask_comparison | 34 | Meminta perbandingan antar mobil |
| ask_similar_car | 19 | Meminta rekomendasi mobil serupa/sekelas |
| **Total** | **850** | |

### 6.2 Distribusi Entity (16 jenis entity, 931 anotasi total)

| Entity | Jumlah Anotasi | Deskripsi |
|---|---|---|
| preference | 198 | Preferensi umum (irit, nyaman, sporty, dsb.) |
| budget | 197 | Anggaran (di bawah 300 juta, 400-500 juta) |
| min_seat | 70 | Jumlah kursi minimal |
| brand | 67 | Merek mobil (Toyota, Honda, Suzuki, dll) |
| feature | 61 | Fitur (sunroof, kamera 360, apple carplay) |
| powertrain | 54 | Jenis penggerak (bensin, diesel, hybrid, listrik, ev) |
| hard_filter | 47 | Filter keras / wajib (keluarga besar, bebas banjir) |
| body_type | 40 | Tipe bodi (SUV, MPV, sedan, hatchback) |
| preference.negated | 38 | Preferensi yang dinegasikan |
| brand.negated | 35 | Merek yang dinegasikan |
| transmission | 31 | Transmisi (matic, manual, cvt, dct) |
| powertrain.negated | 30 | Jenis penggerak yang dinegasikan |
| transmission.negated | 26 | Transmisi yang dinegasikan |
| target_car | 19 | Mobil target spesifik (Avanza, Xpander, dll) |
| body_type.negated | 11 | Tipe bodi yang dinegasikan |
| feature.negated | 7 | Fitur yang dinegasikan |
| **Total** | **931** | (beberapa kalimat memiliki multiple entity) |

### 6.3 Rangkuman Komponen per Konfigurasi (dari file YAML aktual)

| Config | Tokenizer | Featurizers | DIET epochs | DIET dropout | RegexEntityExtractor | FallbackClassifier |
|---|---|---|---|---|---|---|
| CP | _default Rasa_ | _default_ (CountVectors char_wb=4, LexicalSyntactic, RegexFeaturizer) | 100 (default) | ❌ | ❌ | threshold=0.3 (default) |
| TAv1 | Whitespace | RegexFeaturizer, LexicalSyntactic, CountVectors (char_wb=3) | 150, lr=0.001, batch=[64,256] | ❌ | ❌ | ❌ |
| TAv2 | Whitespace | IndoBERT, RegexFeaturizer | 50, lr=0.001 | ❌ | ❌ | ❌ |
| TAv3 | Whitespace | RegexFeaturizer, LexicalSyntactic, CountVectors (char_wb=3) | 100, lr=0.001 | **0.2** | ✅ | ❌ |
| TAv4 | Whitespace | IndoBERT, RegexFeaturizer | 75, lr=0.001, batch=[64,256] | ❌ | ✅ | threshold=0.6 |
| TAv5 | Whitespace | IndoBERT, RegexFeaturizer | 75, lr=0.001, batch=[64,256] | **0.2** | ✅ | threshold=0.4 |
| TAv6 | Whitespace | IndoBERT, RegexFeaturizer, LexicalSyntactic, CountVectors (char_wb=3) | 150, lr=0.001, batch=[64,256] | ❌ | ❌ | threshold=0.4 |

**Catatan penting:**
- CP menggunakan `pipeline:` tanpa isi (semua di-comment di configCP.yml), sehingga Rasa secara otomatis menggunakan default pipeline.
- TAv5 identik dengan TAv4 **kecuali** penambahan `dropout_rate: 0.2` dan penurunan threshold dari 0.6 menjadi 0.4.
- TAv6 **tidak** menggunakan RegexEntityExtractor (sengaja dihapus agar tidak bentrok dengan DIET yang sudah kuat berkat hybrid featurizer).
- Overfit verdict pada CSV menggunakan threshold: gap > 0.15 = OVERFIT, gap > 0.05 = SEDIKIT OVERFIT, sisanya = GENERALISASI BAIK.
