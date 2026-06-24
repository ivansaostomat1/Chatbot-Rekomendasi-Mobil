# Konteks Penelitian: Optimasi Pipeline Rasa NLU — Pendekatan CRISP-ML(Q)

Dokumen ini merupakan kompilasi dari seluruh konfigurasi, skrip eksekusi eksperimen, alat ekstraksi, serta data hasil pengujian yang dilakukan dalam proses optimasi pipeline Rasa NLU. Struktur dokumen mengikuti kerangka metodologi **CRISP-ML(Q)** (_Cross-Industry Standard Process for Machine Learning with Quality Assurance_) yang terdiri dari 6 fase.

Dokumen ini tidak memuat klaim atau teori baru, melainkan hanya menjabarkan **apa yang telah dilakukan** di dalam kode dan **apa hasil dari metrik pengujian** yang didapat, sehingga dapat menjadi acuan (konteks) yang akurat.

---

## Fase 1: Business & Data Understanding

### 1.1 Tujuan Bisnis (Business Objective)

Mengembangkan dan mengoptimasi pipeline NLU (Natural Language Understanding) pada framework Rasa untuk chatbot rekomendasi mobil berbahasa Indonesia. Chatbot harus mampu:

1. **Mengklasifikasikan intent** pengguna secara akurat (misalnya: meminta rekomendasi, membandingkan mobil, menyatakan preferensi).
2. **Mengekstraksi entity** dari kalimat pengguna, termasuk entitas bernegasi (misalnya: "jangan SUV", "bukan diesel") yang mengandung penolakan terhadap suatu kriteria.

### 1.2 Success Criteria (KPI)

| KPI | Deskripsi | Threshold |
| --- | --------- | --------- |
| **Intent F1-Score** | Rata-rata _weighted F1-Score_ klasifikasi intent | ≥ 0.88 |
| **Entity F1-Score** | Rata-rata _weighted F1-Score_ ekstraksi entity | ≥ 0.90 |
| **Overfitting Gap** | Selisih F1-Score antara data latih dan data uji silang | Gap ≤ 0.05 → GOOD FIT |
| **Stabilitas** | Standar deviasi F1-Score antar fold cross-validation | Std ≤ 0.01 |

Verdiksi overfitting menggunakan threshold:
- Gap > 0.15 → **OVERFIT**
- Gap > 0.05 → **SEDIKIT OVERFIT**
- Gap ≤ 0.05 → **GOOD FIT**

### 1.3 Deskripsi Dataset (Ground Truth dari `data/nlu.yml`)

**PENTING:** Angka-angka di bawah ini dihitung langsung dari file `data/nlu.yml` yang digunakan saat eksperimen. Angka-angka ini adalah sumber kebenaran (_ground truth_) yang harus menjadi rujukan utama jika terjadi inkonsistensi dengan dokumen lain.

#### 1.3.1 Distribusi Intent (6 intent, 903 kalimat total)

| Intent             | Jumlah Sampel | Deskripsi                                   |
| ------------------ | ------------- | ------------------------------------------- |
| choose_preference  | 334           | Menyatakan preferensi (suka/tidak suka)     |
| ask_recommendation | 297           | Meminta rekomendasi mobil                   |
| start_search       | 121           | Memulai pencarian mobil / reset             |
| out_of_scope       | 97            | Pertanyaan di luar domain rekomendasi mobil |
| ask_comparison     | 34            | Meminta perbandingan antar mobil            |
| ask_similar_car    | 20            | Meminta rekomendasi mobil serupa/sekelas    |
| **Total**          | **903**       |                                             |

#### 1.3.2 Distribusi Entity (16 jenis entity, 932 anotasi total)

| Entity               | Jumlah Anotasi | Deskripsi                                             |
| -------------------- | -------------- | ----------------------------------------------------- |
| preference           | 198            | Preferensi umum (irit, nyaman, sporty, dsb.)          |
| budget               | 197            | Anggaran (di bawah 300 juta, 400-500 juta)            |
| min_seat             | 70             | Jumlah kursi minimal                                  |
| brand                | 67             | Merek mobil (Toyota, Honda, Suzuki, dll)               |
| feature              | 61             | Fitur (sunroof, kamera 360, apple carplay)            |
| powertrain           | 54             | Jenis penggerak (bensin, diesel, hybrid, listrik, ev) |
| hard_filter          | 47             | Filter keras / wajib (keluarga besar, bebas banjir)   |
| body_type            | 40             | Tipe bodi (SUV, MPV, sedan, hatchback)                |
| preference.negated   | 38             | Preferensi yang dinegasikan                           |
| brand.negated        | 35             | Merek yang dinegasikan                                |
| transmission         | 31             | Transmisi (matic, manual, cvt, dct)                   |
| powertrain.negated   | 30             | Jenis penggerak yang dinegasikan                      |
| transmission.negated | 26             | Transmisi yang dinegasikan                            |
| target_car           | 20             | Mobil target spesifik (Avanza, Xpander, dll)          |
| body_type.negated    | 11             | Tipe bodi yang dinegasikan                            |
| feature.negated      | 7              | Fitur yang dinegasikan                                |
| **Total**            | **932**        | (beberapa kalimat memiliki multiple entity)           |

#### 1.3.3 Distribusi Lookup Table (8 tabel pencarian, 109 entri total)

Untuk mendukung ekstraksi entitas, terdapat 8 *lookup table* yang didefinisikan di dalam dataset NLU:

| Lookup Table  | Jumlah Entri | Contoh Kata Kunci |
| ------------- | ------------ | ----------------- |
| preference    | 51           | irit, hemat, kencang, nyaman, empuk, senyap, luas |
| brand         | 16           | toyota, honda, suzuki, mitsubishi, bmw, mercedes |
| budget        | 15           | 100 jutaan, 200jt, 500jt, 1M, 2M |
| transmission  | 7            | manual, matic, cvt, dct, amt, single speed, dht |
| body_type     | 6            | suv, mpv, sedan, hatchback, coupe, wagon |
| feature       | 6            | sunroof, panoramic sunroof, apple carplay, android auto |
| powertrain    | 5            | hybrid, bensin, diesel, listrik, ev |
| hard_filter   | 3            | keluarga besar, bebas banjir, banjir |
| **Total**     | **109**      |                   |

### 1.4 Identifikasi Risiko

| Risiko | Dampak | Mitigasi |
| ------ | ------ | -------- |
| Ketidakseimbangan kelas (class imbalance) | Intent `ask_similar_car` (20 sampel) vs `choose_preference` (334 sampel) → bias prediksi | Evaluasi per-kelas (bukan hanya weighted avg) |
| Entitas negasi sangat sedikit | `feature.negated` hanya 7 anotasi → sulit dipelajari model | Monitoring khusus performa entitas negasi |
| Overfitting pada dataset kecil | Model menghafal pola training → performa turun di data baru | Overfit detection (gap train vs CV) |

---

## Fase 2: Data Engineering (Data Preparation)

### 2.1 Format Data

Data NLU disimpan dalam format YAML standar Rasa (`data/nlu.yml`) dengan skema sebagai berikut:

```yaml
# Contoh format data NLU
nlu:
  - intent: ask_recommendation
    examples: |
      - carikan mobil [SUV](body_type) [di bawah 300 juta](budget)
      - saya mau mobil [bukan diesel](powertrain.negated) yang [irit](preference)

  - intent: choose_preference
    examples: |
      - saya [tidak mau](preference.negated) yang [boros](preference.negated)
      - [jangan Toyota](brand.negated), yang penting [ada sunroof](feature)
```

### 2.2 Skema Anotasi Entity

Entity dianotasi menggunakan dua format:
1. **Format sederhana**: `[nilai](entity)` — contoh: `[SUV](body_type)`
2. **Format negasi**: `[nilai](entity.negated)` — contoh: `[bukan diesel](powertrain.negated)`

Entity negasi (`*.negated`) digunakan untuk menangkap penolakan pengguna terhadap suatu kriteria, yang merupakan tantangan utama NLU dalam domain ini.

### 2.3 Strategi Evaluasi

- **Metode**: 5-Fold Cross-Validation (K=5)
- **Pengulangan**: 3 kali putaran (run) per konfigurasi untuk mengukur stabilitas
- **Overfit Detection**: Model dilatih pada seluruh dataset, lalu diuji ulang pada data latih yang sama. Selisih F1-Score antara evaluasi data latih dan rata-rata CV digunakan sebagai indikator overfitting.

### 2.4 Pembagian Data

Pembagian data dilakukan secara otomatis oleh Rasa menggunakan stratified split pada setiap fold cross-validation, memastikan distribusi intent yang proporsional di setiap fold.

---

## Fase 3: Machine Learning Model Engineering

### 3.1 Desain Eksperimen

Terdapat **7 konfigurasi pipeline** yang diujikan, masing-masing dengan strategi dan fokus yang berbeda. Semua konfigurasi menggunakan `recipe: default.v1` dan `language: id`.

### 3.2 Rangkuman Komponen per Konfigurasi

| Config  | Tokenizer        | Featurizers                                                             | DIET epochs                   | DIET dropout  | RegexEntityExtractor | FallbackClassifier      |
| ------- | ---------------- | ----------------------------------------------------------------------- | ----------------------------- | ------------- | -------------------- | ----------------------- |
| Default | _default Rasa_   | _default_ (CountVectors char_wb=4, LexicalSyntactic, RegexFeaturizer)   | 100 (default)                 | ❌            | ❌                   | threshold=0.3 (default) |
| TAv1    | Whitespace       | RegexFeaturizer, LexicalSyntactic, CountVectors (char_wb=3)             | 150, lr=0.001, batch=[64,256] | ❌            | ❌                   | ❌                      |
| TAv2    | Whitespace       | IndoBERT, RegexFeaturizer                                               | 50, lr=0.001                  | ❌            | ❌                   | ❌                      |
| TAv3    | Whitespace       | RegexFeaturizer, LexicalSyntactic, CountVectors (char_wb=3)             | 100, lr=0.001                 | **0.2**       | ✅                   | ❌                      |
| TAv4    | Whitespace       | IndoBERT, RegexFeaturizer                                               | 75, lr=0.001, batch=[64,256]  | ❌            | ✅                   | threshold=0.6           |
| TAv5    | Whitespace       | IndoBERT, RegexFeaturizer                                               | 75, lr=0.001, batch=[64,256]  | **0.2**       | ✅                   | threshold=0.4           |
| TAv6    | Whitespace       | IndoBERT, RegexFeaturizer, LexicalSyntactic, CountVectors (ngram=2, char_wb=3) | 150, lr=0.001, batch=[32,128] | **0.15**      | ✅                   | threshold=0.4           |

**Catatan penting:**

- Default menggunakan `pipeline:` tanpa isi (semua di-comment di configDefault.yml), sehingga Rasa secara otomatis menggunakan default pipeline.
- TAv5 identik dengan TAv4 **kecuali** penambahan `dropout_rate: 0.2` dan penurunan threshold dari 0.6 menjadi 0.4.
- TAv6 menggunakan arsitektur hybrid featurizer yang digabungkan dengan **RegexEntityExtractor**, **dropout_rate: 0.15**, dan ukuran batch **[32, 128]** untuk optimalisasi performa pada kelas minoritas.

### 3.3 Detail Konfigurasi Pipeline (YAML)

#### 3.3.1 configDefault.yml (Baseline)

```yaml
==================================================
 SECTION: configDefault.yml (Baseline)
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
```

#### 3.3.2 configTAv1.yml — Hyperparameter Tuning Only

Fokus: optimasi parameter DIET tanpa mengubah komponen pipeline.

```yaml
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
```

#### 3.3.3 configTAv2.yml — IndoBERT (HuggingFace Transformers) Only

Fokus: mengganti seluruh featurizer ke pre-trained IndoBERT (`indobenchmark/indobert-base-p1`).

```yaml
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
```

#### 3.3.4 configTAv3.yml — CountVectors + RegexEntityExtractor + LexicalSyntactic

Fokus: memperkuat deteksi negasi dengan rule-based tanpa Spacy.

```yaml
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
```

#### 3.3.5 configTAv4.yml — IndoBERT + RegexEntityExtractor

Fokus: kontekstual semantik (IndoBERT) + rule-based fallback (Regex).

```yaml
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
```

#### 3.3.6 configTAv5.yml — IndoBERT + RegexEntityExtractor + Regularization

Fokus: mencegah overfitting dari TAv4 dengan menambahkan `dropout_rate: 0.2` pada DIETClassifier.

```yaml
==================================================
 SECTION: configTAv5.yml 
==================================================

recipe: default.v1
language: id

# TAv5 — IndoBERT + RegexEntityExtractor + Regularization
# Fokus: Mencegah overfitting dari TAv4 dengan menambahkan dropout_rate: 0.2 pada DIETClassifier.

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
```

#### 3.3.7 configTAv6.yml — Hybrid Featurizer (IndoBERT + N-Gram)

Fokus: menggabungkan kekuatan semantik IndoBERT dengan sensitivitas n-gram/imbuhan dari CountVectors dan LexicalSyntacticFeaturizer, dipadu dengan epochs 150.

```yaml
==================================================
 SECTION: configTAv6.yml 
==================================================

recipe: default.v1
language: id

pipeline:
  - name: WhitespaceTokenizer
    intent_tokenization_flag: false
    intent_split_symbol: "_"

  # 1. IndoBERT untuk Intent Contextual Understanding
  - name: LanguageModelFeaturizer
    model_name: "bert"
    model_weights: "indobenchmark/indobert-base-p1"

  - name: RegexFeaturizer
  
  # 2. LexicalSyntacticFeaturizer (Untuk mendeteksi posisi "tanpa"/"bukan")
  - name: LexicalSyntacticFeaturizer
  
  # 3. CountVectors (Sparse feature) untuk ketajaman entity boundaries
  - name: CountVectorsFeaturizer
    min_ngram: 1
    max_ngram: 2   # Diperluas ke bigram untuk menangkap kombinasi negasi leksikal
  - name: CountVectorsFeaturizer
    analyzer: char_wb
    min_ngram: 1
    max_ngram: 3   # Menggunakan 3 seperti di TAv1 untuk mengurangi noise

  # 4. DIETClassifier (Tuned untuk dataset kecil)
  - name: DIETClassifier
    epochs: 150
    learning_rate: 0.001
    batch_size: [32, 128]      # Diperkecil untuk update bobot lebih sering pada data terbatas
    dropout_rate: 0.15          # Regularisasi ringan untuk membantu generalisasi entitas minoritas
    constrain_similarities: true
    entity_recognition: true

  - name: EntitySynonymMapper
  
  # 5. RegexEntityExtractor (Pencegahan kegagalan ekstraksi entitas minoritas/negasi via lookup tables)
  - name: RegexEntityExtractor
    use_lookup_tables: true
    use_regexes: true
    use_word_boundaries: true
  
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

## Fase 4: Quality Assurance (Evaluation)

### 4.1 Skrip Pengujian Silang (Cross-Validation) & Deteksi Overfit

**File:** `eval_a.py`, `eval_s.py`, dan `check_overfit.py`
**Kegunaan di Penelitian:**
Skrip otomatisasi untuk menjalankan proses _Cross-Validation_ (evaluasi data lipat-silang) secara konsisten dan transparan. Skrip `eval_a.py` menguji seluruh daftar file konfigurasi (Default, TAv1-TAv6) secara bergantian dengan 3 putaran (run), sementara `eval_s.py` khusus untuk satu konfigurasi saja. Selain itu, terdapat skrip pendukung `check_overfit.py` yang berfungsi khusus untuk memonitor dengan cepat tingkat *overfit/underfit* seluruh konfigurasi menggunakan 1 kali putaran CV saja lalu mencetak ringkasan hasilnya. Ketiga skrip ini melakukan tugas penting berupa:

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
    ("Default", "configDefault.yml"),
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

### 4.2 Ekstraksi dan Kompilasi Metrik

**File:** `ekstrak.py`
**Kegunaan di Penelitian:**
Mengekstrak hasil metrik _F1-score_ yang tersebar di ratusan file JSON (seperti `intent_report.json` dan `DIETClassifier_report.json`) yang dihasilkan oleh Rasa. Skrip ini menghitung nilai rata-rata (_mean_) dan standar deviasi sampel dari seluruh pengulangan _Cross-Validation_, serta membuat dua file format CSV (`comparison_overview.csv` dan `comparison_detail.csv`) yang merangkum keseluruhan performa masing-masing model untuk _Intent_ dan _Entity_.

```python
# Potongan kode utama dari ekstrak.py
import os, json, csv, glob
from statistics import mean, stdev

RESULTS_DIR = "results/baru"
OUTPUT_CSV = "comparison_overview.csv"

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
    # Menulis ke file comparison_overview.csv (overall) dan comparison_detail.csv (per kelas)
    pass
```

### 4.3 Pembuatan Visualisasi Data Evaluasi

**File:** `generate_plots.py`
**Kegunaan di Penelitian:**
Mengolah data agregat dari CSV hasil ekstraksi (`comparison_overview.csv` dan `comparison_detail.csv`) ke dalam bentuk bagan untuk analisis Bab 4 penelitian. Visualisasi ini (bar chart, line chart, scatter plot, radar chart, dan confusion matrix) mempermudah identifikasi kualitatif konfigurasi mana yang paling andal, konsisten, dan memiliki generalisasi tinggi tanpa terjadinya _overfit_ yang ekstrem.

```python
# Potongan kode utama dari generate_plots.py
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

RESULTS_DIR = r"results\baru"
OUTPUT_DIR = r"gambar bab 4"
df_summary = pd.read_csv(os.path.join(RESULTS_DIR, "comparison_overview.csv"))
df_detail = pd.read_csv(os.path.join(RESULTS_DIR, "comparison_detail.csv"))

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

### 4.4 Hasil Pengujian / Data Hasil Eksperimen

**Folder:** `results/baru`
**Kegunaan di Penelitian:**
Ini adalah hasil nyata (empiris) dari komputasi evaluasi. Data dalam bentuk CSV di bawah ini merupakan metrik perbandingan performa masing-masing dari tujuh konfigurasi yang diuji.

#### File 1: `comparison_overview.csv` (Ikhtisar Performa Secara Keseluruhan)

Berisi Rata-Rata _F1-Score_, _Precision_, _Recall_ dan Standar Deviasi (stabilitas) untuk Intent dan Entity dari 3 kali _Cross-Validation_. Juga terdapat nilai perbandingan dengan evaluasi data _Training_ untuk mendeteksi seberapa parah gap _Overfitting_-nya, serta durasi waktu komputasi.

```csv
config,intent_f1_mean,intent_f1_std,intent_precision_mean,intent_precision_std,intent_recall_mean,intent_recall_std,entity_f1_mean,entity_f1_std,entity_precision_mean,entity_precision_std,entity_recall_mean,entity_recall_std,train_intent_f1,gap(train-cv),status_overfit,num_cv_runs
Default,0.8783,0.0099,0.8818,0.0096,0.8788,0.0099,0.9062,0.0024,0.8956,0.0024,0.9206,0.0037,0.8751,-0.0032,GOOD FIT,3
TAv1,0.8854,0.006,0.8889,0.0047,0.8862,0.0056,0.9074,0.0051,0.8969,0.0078,0.9215,0.0042,0.7216,-0.1638,GOOD FIT,3
TAv2,0.8986,0.0031,0.8997,0.003,0.8995,0.0028,0.8905,0.0037,0.9042,0.0032,0.8869,0.0049,0.9622,0.0636,SEDIKIT OVERFIT,3
TAv3,0.8796,0.003,0.8825,0.0038,0.8802,0.0032,0.9044,0.0031,0.8946,0.0036,0.9194,0.0061,0.99,0.1104,SEDIKIT OVERFIT,3
TAv4,0.9001,0.0116,0.9016,0.0115,0.9014,0.0114,0.9053,0.0029,0.9134,0.0046,0.903,0.0028,0.8088,-0.0913,GOOD FIT,3
TAv5,0.8917,0.0094,0.8945,0.0077,0.8932,0.0088,0.9016,0.0061,0.9131,0.0085,0.8977,0.0051,0.8008,-0.0909,GOOD FIT,3
TAv6,0.8991,0.0071,0.8999,0.0068,0.8991,0.0072,0.9186,0.0055,0.92,0.0018,0.9206,0.0075,1.0,0.1009,SEDIKIT OVERFIT,3
```

#### File 2: `comparison_detail.csv` (Performa Per Kelas / Label)

Memperlihatkan performa _F1-score_, _Precision_, _Recall_ rata-rata dan standar deviasinya di level yang lebih mikroskopis (per spesifik intent dan entitas). Hal ini krusial untuk mengamati misalnya peningkatan performa entitas negasi (`body_type.negated`, `feature.negated`, dsb).

```csv
type,class,Default_f1,Default_f1_std,Default_precision,Default_precision_std,Default_recall,Default_recall_std,TAv1_f1,TAv1_f1_std,TAv1_precision,TAv1_precision_std,TAv1_recall,TAv1_recall_std,TAv2_f1,TAv2_f1_std,TAv2_precision,TAv2_precision_std,TAv2_recall,TAv2_recall_std,TAv3_f1,TAv3_f1_std,TAv3_precision,TAv3_precision_std,TAv3_recall,TAv3_recall_std,TAv4_f1,TAv4_f1_std,TAv4_precision,TAv4_precision_std,TAv4_recall,TAv4_recall_std,TAv5_f1,TAv5_f1_std,TAv5_precision,TAv5_precision_std,TAv5_recall,TAv5_recall_std,TAv6_f1,TAv6_f1_std,TAv6_precision,TAv6_precision_std,TAv6_recall,TAv6_recall_std
intent,ask_comparison,0.8774,0.0058,0.9176,0.0421,0.8431,0.0449,0.9074,0.0304,0.9031,0.033,0.9118,0.0294,0.9264,0.0571,0.9773,0.0197,0.8824,0.0882,0.8669,0.0538,0.8984,0.1172,0.8431,0.017,0.9325,0.0652,0.9672,0.0346,0.902,0.0945,0.8733,0.0338,0.9429,0.0208,0.8137,0.0449,0.9026,0.0267,0.9049,0.0581,0.902,0.017
intent,ask_recommendation,0.8594,0.0123,0.8394,0.0208,0.8806,0.0052,0.8639,0.0075,0.849,0.0099,0.8795,0.0141,0.8823,0.0026,0.891,0.0081,0.8739,0.0119,0.8593,0.004,0.8486,0.0054,0.8705,0.0137,0.8855,0.0142,0.8976,0.0259,0.8739,0.0039,0.8748,0.0045,0.8885,0.0062,0.8615,0.0059,0.8744,0.01,0.8785,0.0127,0.8705,0.0109
intent,ask_similar_car,0.7669,0.0503,0.9744,0.0444,0.6333,0.0577,0.7626,0.0219,1.0,0.0,0.6167,0.0289,0.683,0.0639,0.8394,0.0632,0.5833,0.1041,0.7416,0.041,0.9744,0.0444,0.6,0.05,0.6456,0.0208,0.8629,0.0405,0.5167,0.0289,0.6549,0.0729,0.9246,0.0718,0.5167,0.1041,0.8576,0.0535,0.9265,0.0795,0.8,0.05
intent,choose_preference,0.8734,0.0075,0.8606,0.0078,0.8865,0.0097,0.8871,0.0047,0.8753,0.0125,0.8996,0.0184,0.8898,0.0041,0.8764,0.0056,0.9036,0.003,0.8801,0.0097,0.8652,0.0075,0.8956,0.0166,0.8955,0.0087,0.8753,0.0014,0.9167,0.0171,0.8912,0.011,0.8635,0.0115,0.9207,0.0106,0.8926,0.0134,0.8801,0.0165,0.9056,0.0155
intent,out_of_scope,0.8644,0.0523,0.9497,0.0356,0.7938,0.0644,0.874,0.0351,0.959,0.0067,0.8041,0.0574,0.9407,0.0134,0.9541,0.0122,0.9278,0.0179,0.8736,0.0304,0.9333,0.0194,0.8213,0.039,0.9183,0.0126,0.9298,0.0204,0.9072,0.0103,0.9024,0.0158,0.9153,0.0178,0.89,0.0157,0.9099,0.0198,0.9388,0.0367,0.8832,0.006
intent,start_search,0.9682,0.0063,0.9642,0.0093,0.9722,0.0048,0.9575,0.0024,0.946,0.0112,0.9694,0.0127,0.9569,0.0062,0.9294,0.0073,0.9861,0.0096,0.96,0.0063,0.9535,0.009,0.9667,0.0083,0.9673,0.0002,0.9492,0.0041,0.9861,0.0048,0.9712,0.0148,0.9594,0.0162,0.9833,0.0144,0.9752,0.0106,0.9702,0.0227,0.9806,0.0048
entity,body_type,0.971,0.0069,0.9671,0.0137,0.975,0.0,0.9667,0.0144,0.9667,0.0144,0.9667,0.0144,0.8996,0.007,0.8684,0.011,0.9333,0.0144,0.946,0.0147,0.9423,0.0134,0.95,0.025,0.9331,0.0267,0.9331,0.0157,0.9333,0.0382,0.9112,0.0079,0.8834,0.018,0.9417,0.0289,0.9304,0.0168,0.9207,0.0471,0.9417,0.0144
entity,body_type.negated,0.9841,0.0275,1.0,0.0,0.9697,0.0525,0.9565,0.0753,0.9444,0.0962,0.9697,0.0525,0.7029,0.0764,1.0,0.0,0.5455,0.0909,0.9091,0.0,0.9091,0.0,0.9091,0.0,0.9,0.0,1.0,0.0,0.8182,0.0,0.7612,0.0492,0.963,0.0642,0.6364,0.0909,0.8474,0.0502,0.963,0.0642,0.7576,0.0525
entity,brand,0.9259,0.0172,0.9532,0.0298,0.9005,0.0172,0.918,0.0079,0.9482,0.0311,0.8905,0.0228,0.8787,0.0153,0.8289,0.028,0.9353,0.0086,0.9265,0.0195,0.9435,0.0225,0.9104,0.0259,0.8869,0.0103,0.8435,0.0225,0.9353,0.0086,0.8933,0.0114,0.856,0.0361,0.9353,0.0228,0.9156,0.0119,0.8878,0.0024,0.9453,0.0228
entity,brand.negated,0.8878,0.0278,0.8718,0.0296,0.9048,0.033,0.9056,0.025,0.8559,0.015,0.9619,0.0436,0.8052,0.034,0.897,0.0247,0.7333,0.066,0.9153,0.0229,0.9076,0.039,0.9238,0.0165,0.8381,0.0139,0.8941,0.0299,0.7905,0.0436,0.8384,0.0091,0.8927,0.0154,0.7905,0.0165,0.8529,0.0393,0.8806,0.0527,0.8286,0.0495
entity,budget,0.9525,0.0058,0.9476,0.01,0.9576,0.0026,0.9595,0.0066,0.9496,0.0107,0.9697,0.0026,0.9695,0.0036,0.9769,0.0044,0.9621,0.0069,0.9597,0.0064,0.9458,0.0145,0.9742,0.0026,0.9734,0.0026,0.9771,0.0045,0.9697,0.0026,0.9696,0.0012,0.9726,0.0044,0.9667,0.0026,0.9698,0.0048,0.9655,0.0027,0.9742,0.0069
entity,feature,0.9475,0.0073,0.9132,0.0156,0.9848,0.0139,0.9705,0.0088,0.9484,0.0212,0.9939,0.0105,0.9606,0.0074,0.9269,0.0121,0.997,0.0052,0.9602,0.0158,0.9367,0.0192,0.9848,0.0139,0.9649,0.0114,0.9349,0.0188,0.997,0.0052,0.9663,0.0088,0.9376,0.0181,0.997,0.0052,0.9689,0.0046,0.9478,0.0005,0.9909,0.0091
entity,feature.negated,0.6908,0.0211,0.8259,0.1557,0.6061,0.0525,0.867,0.043,0.9487,0.0888,0.8182,0.1575,0.5448,0.144,0.9333,0.1155,0.3939,0.1389,0.7377,0.2097,0.9091,0.1575,0.6667,0.2777,0.6637,0.1005,0.9444,0.0962,0.5152,0.105,0.5601,0.2195,0.9524,0.0825,0.4242,0.2099,0.7612,0.0492,0.963,0.0642,0.6364,0.0909
entity,hard_filter,0.9838,0.0053,0.9682,0.0103,1.0,0.0,0.9873,0.0031,0.975,0.006,1.0,0.0,0.9837,0.0093,0.9715,0.0122,0.9963,0.0063,0.9856,0.0061,0.9716,0.0119,1.0,0.0,0.9835,0.0055,0.9818,0.0063,0.9853,0.0063,0.9873,0.0032,0.9784,0.0001,0.9963,0.0063,0.9891,0.0054,0.9786,0.0105,1.0,0.0
entity,min_seat,0.8619,0.0181,0.802,0.0357,0.9324,0.0084,0.8787,0.0071,0.8351,0.0155,0.9275,0.0145,0.9808,0.0042,0.9716,0.0002,0.9903,0.0084,0.8632,0.0146,0.8196,0.0348,0.913,0.0251,0.988,0.0042,0.981,0.008,0.9952,0.0084,0.976,0.0109,0.9714,0.0142,0.9807,0.0084,0.974,0.0108,0.9538,0.0156,0.9952,0.0084
entity,powertrain,0.9483,0.0108,0.9342,0.0098,0.963,0.0185,0.931,0.0044,0.9071,0.0222,0.9568,0.0214,0.9139,0.0113,0.8803,0.0132,0.9506,0.0283,0.9339,0.0201,0.9125,0.0326,0.9568,0.0214,0.9112,0.0159,0.8749,0.0111,0.9506,0.0214,0.9165,0.0235,0.8854,0.0235,0.9506,0.0385,0.9248,0.0194,0.9005,0.0116,0.9506,0.0283
entity,powertrain.negated,0.9413,0.0179,0.9078,0.0284,0.9778,0.0192,0.9312,0.0092,0.8891,0.0149,0.9778,0.0192,0.8979,0.0156,0.9198,0.0374,0.8778,0.0192,0.9413,0.0179,0.9078,0.0284,0.9778,0.0192,0.862,0.018,0.8938,0.0299,0.8333,0.0333,0.8801,0.0152,0.9071,0.035,0.8556,0.0192,0.922,0.0359,0.9228,0.0373,0.9222,0.0509
entity,preference,0.811,0.0157,0.7885,0.0213,0.8348,0.0095,0.7977,0.0074,0.7731,0.0174,0.8242,0.0095,0.7842,0.0211,0.8063,0.0117,0.7636,0.0318,0.7908,0.0109,0.7619,0.0095,0.8227,0.0355,0.8006,0.0141,0.8044,0.0171,0.797,0.0114,0.8032,0.0091,0.8226,0.0193,0.7848,0.0095,0.8136,0.0095,0.8136,0.008,0.8136,0.012
entity,preference.negated,0.9084,0.0182,0.8654,0.0245,0.9561,0.0152,0.8996,0.0601,0.8879,0.0428,0.9123,0.0804,0.9691,0.0079,0.9734,0.0004,0.9649,0.0152,0.9447,0.0069,0.9175,0.013,0.9737,0.0,0.9732,0.0004,0.9912,0.0152,0.9561,0.0152,0.9865,0.0135,1.0,0.0,0.9737,0.0263,0.9647,0.0072,0.9739,0.0257,0.9561,0.0152
entity,target_car,0.7226,0.0253,0.9153,0.0349,0.5972,0.0241,0.7495,0.0313,0.9373,0.0039,0.625,0.0417,0.6202,0.0869,0.9667,0.0577,0.4583,0.0833,0.6605,0.0205,0.9249,0.0032,0.5139,0.0241,0.6832,0.0541,0.9762,0.0412,0.5278,0.0636,0.7136,0.091,0.9815,0.0321,0.5694,0.1273,0.7708,0.0638,0.9804,0.034,0.6389,0.0867
entity,transmission,0.9325,0.0103,0.9282,0.0143,0.9375,0.0312,0.8962,0.0521,0.8898,0.0534,0.9062,0.0827,0.8242,0.016,0.7965,0.0236,0.8542,0.018,0.9428,0.0192,0.9381,0.0023,0.9479,0.0361,0.8723,0.0159,0.8914,0.0178,0.8542,0.018,0.8181,0.0647,0.8139,0.0558,0.8229,0.0786,0.9534,0.0308,0.9488,0.0344,0.9583,0.0361
entity,transmission.negated,0.9268,0.0343,0.9293,0.069,0.9259,0.0,0.9002,0.0374,0.9171,0.0726,0.8889,0.0642,0.779,0.0253,0.822,0.0203,0.7407,0.037,0.932,0.0198,0.9386,0.0397,0.9259,0.0,0.8553,0.0113,0.8722,0.0177,0.8395,0.0214,0.8338,0.0367,0.8681,0.0555,0.8025,0.0214,0.9482,0.0244,0.9877,0.0214,0.9136,0.0566
```

---

## Fase 5: Deployment

### 5.1 Pemilihan Model untuk Deployment

Berdasarkan hasil evaluasi pada Fase 4, pemilihan konfigurasi optimal untuk deployment mempertimbangkan:

1. **Performa keseluruhan** (Intent F1 + Entity F1 tertinggi).
2. **Generalisasi** (overfit verdict = GOOD FIT atau gap rendah).
3. **Stabilitas** (standar deviasi rendah antar fold CV).
4. **Kemampuan menangkap entitas negasi** (performa pada kelas `*.negated`).

Konfigurasi **TAv6** dipilih sebagai model utama deployment karena:
- Intent F1 tertinggi: **0.8991** (SEDIKIT OVERFIT)
- Entity F1 tertinggi: **0.9186** (SEDIKIT OVERFIT)
- Performa `feature.negated` terbaik di antara konfigurasi hybrid: **0.7612**
- Gap train-CV: **0.1009** (model sedikit overfit)

### 5.2 Proses Deployment

Model Rasa NLU yang telah dilatih menggunakan konfigurasi terpilih di-deploy melalui:

1. **Training final**: `rasa train nlu --config configTAv6.yml --nlu data/nlu.yml`
2. **Serving**: Model di-serve melalui Rasa Server yang terintegrasi dengan backend aplikasi chatbot.
3. **Integrasi**: Pipeline NLU terhubung dengan komponen dialog management (Rasa Core) dan backend rekomendasi mobil.

---

## Fase 6: Monitoring & Maintenance

### 6.1 Strategi Monitoring

| Aspek | Metode | Frekuensi |
| ----- | ------ | --------- |
| **Confidence Score** | Logging confidence setiap prediksi intent | Real-time |
| **Fallback Rate** | Persentase pesan yang jatuh ke `out_of_scope` / fallback | Mingguan |
| **Entity Extraction Accuracy** | Spot-check manual pada entitas yang diekstrak | Bulanan |
| **User Feedback** | Feedback implisit (apakah user lanjut atau restart) | Berkelanjutan |

### 6.2 Rencana Re-training

Re-training model dijadwalkan atau dipicu ketika:

1. **Data Drift**: Muncul pola kalimat baru yang tidak tercakup dalam training data (misalnya: tipe mobil baru, fitur baru).
2. **Penurunan Performa**: Fallback rate meningkat signifikan (> 15%) atau confidence score rata-rata menurun.
3. **Penambahan Kapabilitas**: Penambahan intent atau entity baru sesuai kebutuhan bisnis.

Proses re-training mengikuti siklus CRISP-ML(Q) kembali dari Fase 2 (Data Engineering) untuk memastikan kualitas data baru sebelum melatih ulang model.
