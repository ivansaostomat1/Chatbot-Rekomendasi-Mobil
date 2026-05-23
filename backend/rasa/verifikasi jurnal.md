# Verifikasi 45 Jurnal Rujukan vs Komponen Backend Rasa

## Inventarisasi Komponen yang Telah Diimplementasikan

Berdasarkan [what have i done.md](file:///c:/capstone/Chatbot-Rekomendasi-Mobil/backend/rasa/what%20have%20i%20done.md), berikut **seluruh komponen** yang digunakan dalam eksperimen Rasa NLU:

| ID | Komponen | Detail | Config yang Memakai |
|---|---|---|---|
| **K1** | Rasa Framework (v3.1) | Open-source conversational AI framework | Semua (CP–TAv6) |
| **K2** | DIETClassifier | Joint intent & entity classifier (Dual Intent Entity Transformer) | Semua (CP–TAv6) |
| **K3** | CountVectorsFeaturizer | Sparse featurizer (word-level + char n-gram `char_wb`) | CP, TAv1, TAv3, TAv6 |
| **K4** | IndoBERT (`LanguageModelFeaturizer`) | Pre-trained `indobenchmark/indobert-base-p1` via HuggingFace | TAv2, TAv4, TAv5, TAv6 |
| **K5** | RegexFeaturizer | Regex pattern-based feature extraction | Semua (CP–TAv6) |
| **K6** | LexicalSyntacticFeaturizer | Prefix/suffix/POS-like windowed features | CP, TAv1, TAv3, TAv6 |
| **K7** | RegexEntityExtractor | Rule-based entity extraction (lookup tables + regex) | TAv3, TAv4, TAv5 |
| **K8** | FallbackClassifier | Out-of-scope / low-confidence fallback handling | CP, TAv4, TAv5, TAv6 |
| **K9** | EntitySynonymMapper | Entity value normalization via synonyms | Semua (CP–TAv6) |
| **K10** | Cross-Validation (K-Fold=5, 3 runs) | Evaluasi model via stratified cross-validation | eval_a.py, eval_s.py |
| **K11** | Overfit Detection (Train-CV Gap) | Deteksi overfitting: tes model pada data latih vs CV | check_overfit.py |
| **K12** | Hyperparameter Tuning | Variasi epochs, learning_rate, batch_size, dropout_rate, threshold | TAv1–TAv6 |
| **K13** | Dropout / Regularization | dropout_rate: 0.2 untuk generalisasi | TAv3, TAv5 |
| **K14** | Negation Entity Handling | Entity roles `.negated` (8 pasangan entitas) | domain.yml, data/nlu.yml |
| **K15** | N-gram (char_wb) tuning | Variasi max_ngram: 4→3 | TAv1, TAv3, TAv6 |
| **K16** | MemoizationPolicy + RulePolicy | Dialogue management policies | TAv1–TAv6 |
| **K17** | TEDPolicy | Transformer Embedding Dialogue Policy (pada CP default) | CP (default) |
| **K18** | Bahasa Indonesia (language: id) | Seluruh pipeline dikonfigurasi untuk Bahasa Indonesia | Semua |
| **K19** | Metrik: F1-score, Precision, Recall, Accuracy | Evaluasi performa | perbandingan.csv |
| **K20** | Confusion Matrix | Visualisasi kesalahan klasifikasi per-kelas | generate_plots.py |
| **K21** | Visualisasi (bar, line, scatter, radar, heatmap) | 9 gambar analisis Bab 4 | generate_plots.py |

---

## Pemetaan Per-Jurnal: Komponen Mana yang Didukung?

### Legenda Status
- ✅ **Langsung Mendukung** — Jurnal memakai komponen yang sama persis / sangat relevan
- 🔶 **Mendukung Konsep** — Jurnal membahas konsep/teknik yang paralel/mendasari komponen kita
- ⬜ **Tidak Langsung Relevan** — Jurnal tidak memakai komponen kita, tapi masih relevan sebagai konteks latar belakang

---

### Kelompok A: Jurnal yang Menggunakan Rasa Framework (K1) Secara Langsung

| No | Jurnal | Komponen yang Didukung | Status |
|---|---|---|---|
| **4** | 17630 (Chatbot emosional mahasiswa, Rasa, NLU 80%) | K1, K2, K19 | ✅ |
| **17** | 411632.1 (DIET+TED+VADER, F1 intent 0.88) | K1, K2, K5, K17, K19 | ✅ |
| **24** | 8316-8323 (Literatur Review: NLP 50%, Rasa 20%) | K1 | ✅ |
| **25** | 16-22 Chatbot NLP (Akurasi 91%, respons 1.65 detik) | K1, K19 | ✅ |
| **26** | ArRASA (DIET Arabic, SMOTE, F1 95%) | K1, K2, K19 | ✅ |
| **27** | KoRASA (DIET-Opt Korea, F1 98.4%) | K1, K2, K12, K19 | ✅ |
| **28** | Feasibility Study (Rasa vs Dialogflow vs Watson) | K1 | ✅ |
| **29** | E-Commerce Review (DIET F1 98.8%) | K1, K2, K19 | ✅ |
| **30** | Talenggoran (CountVector + LogReg + Fallback 0.7) | K1, K3, K8, K19 | ✅ |
| **31** | 26.4732 (DIET, Flask, Akurasi 91.5%) | K1, K2, K19 | ✅ |
| **32** | AI Chatbot Rasa NLU + Deep Learning + Stress Test | K1, K2 | ✅ |
| **33** | 9a22b (Rasa, 47 intent, Telegram) | K1, K2 | ✅ |
| **34** | RASA 2 (DIET, CRISP-DM, Flask, acc 0.94) | K1, K2, K19, K20 | ✅ |
| **35** | RASA 3 (DIET, 5-fold CV, akurasi 0.825) | K1, K2, K10, K19 | ✅ |
| **36** | RASA 1 (DIET + RegexFeaturizer + LexicalSyntactic) | K1, K2, K5, K6, K19 | ✅ |
| **37** | DIET + embeddings (BERT, DistilBERT, XLNet, GloVe) | K1, K2, K4(konsep), K19 | ✅ |
| **38** | 1712.05181 (Rasa NLU & Core, Machine Teaching) | K1, K2, K16 | ✅ |
| **39** | 2004.09936 (DIET paper asli, sparse+dense, masking) | K1, K2, K3, K19 | ✅ |
| **41** | Tesis RCT (Rasa + RAG + LLM, Multi-Stage Fallback) | K1, K2, K8, K19 | ✅ |

> **Total: 19 jurnal langsung memakai Rasa/DIET** → menjadi tulang punggung justifikasi pemakaian framework dan arsitektur pipeline.

---

### Kelompok B: Jurnal tentang IndoBERT / Pre-trained Language Model Indonesia (K4)

| No | Jurnal | Komponen yang Didukung | Status |
|---|---|---|---|
| **18** | 2020.coling-main.66 (IndoBERT pre-training, 7 tugas NLU) | K4, K18 | ✅ |
| **19** | Sentiment Healthcare (IndoBERT fine-tuning, akurasi 96%) | K4, K18, K19 | ✅ |
| **20** | ABSA Indonesian IndoBERT (F1 0.9194) | K4, K18, K19 | ✅ |
| **21** | el-16-03-09 (IndoBERT vs SVM vs NB, akurasi 94.66%) | K4, K18, K19 | ✅ |
| **22** | Artikel IndoBERT fine-tuning (akurasi 92.52%, imbalanced) | K4, K13(konsep imbalanced), K18, K19 | ✅ |
| **11** | publish fix (IndoBERT terbaik akurasi 0.96, Stratified 10-Fold) | K4, K10, K18, K19 | ✅ |
| **45** | 16037 (IndoBERTweet, preprocessing variasi, F1 0.77) | K4(konsep IndoBERT family), K18, K19 | ✅ |

> **Total: 7 jurnal tentang IndoBERT** → memvalidasi keputusan menggunakan `indobenchmark/indobert-base-p1` sebagai `LanguageModelFeaturizer` pada TAv2/TAv4/TAv5/TAv6.

---

### Kelompok C: Jurnal tentang Teknik Imbalanced Data / SMOTE / Oversampling (relevan ke K10, K11, K13, K14)

| No | Jurnal | Komponen yang Didukung | Status |
|---|---|---|---|
| **5** | 17439 (CRISP-DM, k-Fold CV 2-10, akurasi 93.70%) | K10, K19 | 🔶 |
| **6** | 22-6877 (TF-IDF, SMOTE, SVM, GridSearchCV) | K12(konsep tuning), K19 | 🔶 |
| **7** | 75610 (CNN, Word2Vec, SMOTE/ADASYN) | K19 | 🔶 |
| **8** | 8313 (SVM+SMOTE vs BiLSTM+Undersampling) | K19 | 🔶 |
| **10** | admin+SURYA (Random Forest+SMOTE, Logistic Regression) | K19 | 🔶 |
| **42** | IJCS Syahwaluddin (BERT, SMOTE, akurasi 85→88%) | K4(konsep BERT), K19 | 🔶 |
| **43** | Optimasi LR+TF-IDF+SMOTE (akurasi 76.9%) | K19 | 🔶 |
| **44** | 176 Syahdana (TF-IDF, MNB, SMOTE, akurasi 0.50) | K19 | 🔶 |

> **Total: 8 jurnal tentang data imbalanced** → mendukung secara konseptual mengapa penelitian ini perlu memperhatikan **distribusi data tidak seimbang** (contoh: entity `feature.negated` hanya 7 sampel, `ask_similar_car` hanya 19 sampel), meskipun penelitian ini TIDAK menggunakan SMOTE/oversampling secara eksplisit, melainkan mengandalkan cross-validation, dropout regularization, dan arsitektur pipeline.

---

### Kelompok D: Jurnal tentang Hyperparameter Tuning / Regularization / Dropout (K12, K13)

| No | Jurnal | Komponen yang Didukung | Status |
|---|---|---|---|
| **12** | 1350-1358 (MLP, CNN, L2 Regularization, Dropout) | K13, K19 | 🔶 |
| **13** | 23121 (1D-CNN, Bi-LSTM, Regularization, Dropout) | K13, K19 | 🔶 |
| **14** | 15276 (IndoRoBERTa, Optuna, Dropout paling berpengaruh) | K4(konsep), K12, K13, K19 | 🔶 |
| **15** | 7774 (SVM, GridSearchCV, recall kelas negatif naik) | K12, K19 | 🔶 |
| **16** | 12727 (Decision Tree, SVM, Stratified K-Fold) | K10, K12, K19 | 🔶 |
| **9** | 16946 (BERT, Augmentasi Data, F1 0.9983) | K4(konsep BERT), K19 | 🔶 |

> **Total: 6 jurnal tentang tuning/regularization** → mendukung keputusan melakukan hyperparameter tuning (epochs, lr, batch_size) dan pemakaian dropout_rate 0.2 pada TAv3 dan TAv5.

---

### Kelompok E: Jurnal tentang NLP / Chatbot secara Umum (Latar Belakang / Literature Review)

| No | Jurnal | Komponen yang Didukung | Status |
|---|---|---|---|
| **1** | Submit Paper LR (SLR 100 publikasi, chatbot e-Gov) | K1(konteks chatbot), K18 | ⬜ |
| **2** | JISSI METOPEN (SLR chatbot emosional & sosial) | K1(konteks chatbot) | ⬜ |
| **3** | Jurnal Mahendra (GLTR: BERT, RAG, LSTM, SVM, Hybrid) | K4(konsep BERT), K18 | 🔶 |
| **23** | dina_oktavia (N-Gram, NW-KNN, TF-IDF) | K3(konsep n-gram), K15 | 🔶 |
| **40** | 10289 (survey chatbot antropomorfisme Gen Y vs Gen Z) | K1(konteks chatbot) | ⬜ |

> **Total: 5 jurnal latar belakang** → mendukung konteks riset chatbot secara umum dan penggunaan NLP untuk bahasa Indonesia.

---

## Ringkasan Verdik Per-Jurnal (Tabel Lengkap 45 Jurnal)

| No | Status | Komponen Terkait | Catatan |
|---|---|---|---|
| 1 | ⬜ Latar belakang | K1 | SLR konteks chatbot e-Gov |
| 2 | ⬜ Latar belakang | K1 | SLR chatbot emosional/sosial |
| 3 | 🔶 Mendukung konsep | K4, K18 | Arsitektur chatbot multibahasa, BERT relevan |
| 4 | ✅ **Langsung** | K1, K2, K19 | Rasa + NLU, domain emosional |
| 5 | 🔶 Mendukung konsep | K10, K19 | k-Fold CV, augmentasi data |
| 6 | 🔶 Mendukung konsep | K12, K19 | GridSearchCV, class imbalance |
| 7 | 🔶 Mendukung konsep | K19 | Oversampling meningkatkan performa |
| 8 | 🔶 Mendukung konsep | K19 | Perbandingan strategi imbalanced |
| 9 | 🔶 Mendukung konsep | K4, K19 | BERT + augmentasi data |
| 10 | 🔶 Mendukung konsep | K19 | SMOTE + Random Forest |
| 11 | ✅ **Langsung** | K4, K10, K18, K19 | IndoBERT + Stratified K-Fold |
| 12 | 🔶 Mendukung konsep | K13, K19 | Dropout regularization |
| 13 | 🔶 Mendukung konsep | K13, K19 | Regularization + Dropout |
| 14 | 🔶 Mendukung konsep | K4, K12, K13, K19 | Dropout paling berpengaruh |
| 15 | 🔶 Mendukung konsep | K12, K19 | Hyperparameter tuning SVM |
| 16 | 🔶 Mendukung konsep | K10, K12, K19 | Stratified K-Fold CV |
| 17 | ✅ **Langsung** | K1, K2, K5, K17, K19 | DIET + TED + VADER di Rasa |
| 18 | ✅ **Langsung** | K4, K18 | IndoBERT foundational paper |
| 19 | ✅ **Langsung** | K4, K18, K19 | IndoBERT fine-tuning healthcare |
| 20 | ✅ **Langsung** | K4, K18, K19 | IndoBERT ABSA Indonesia |
| 21 | ✅ **Langsung** | K4, K18, K19 | IndoBERT vs klasik (SVM, NB) |
| 22 | ✅ **Langsung** | K4, K18, K19 | IndoBERT + imbalanced data |
| 23 | 🔶 Mendukung konsep | K3, K15 | N-Gram, TF-IDF (konsep dasar) |
| 24 | ✅ **Langsung** | K1 | Literatur Review dominasi Rasa 20% |
| 25 | ✅ **Langsung** | K1, K19 | Chatbot NLP akurasi 91% |
| 26 | ✅ **Langsung** | K1, K2, K19 | DIET untuk bahasa Arab (ArRASA) |
| 27 | ✅ **Langsung** | K1, K2, K12, K19 | DIET tuning untuk bahasa Korea (KoRASA) |
| 28 | ✅ **Langsung** | K1 | Rasa terbaik untuk privasi & kustomisasi |
| 29 | ✅ **Langsung** | K1, K2, K19 | DIET F1 98.8% e-commerce |
| 30 | ✅ **Langsung** | K1, K3, K8, K19 | CountVector + FallbackClassifier |
| 31 | ✅ **Langsung** | K1, K2, K19 | DIET + Flask akurasi 91.5% |
| 32 | ✅ **Langsung** | K1, K2 | Rasa + Deep Learning |
| 33 | ✅ **Langsung** | K1, K2 | Rasa + Telegram |
| 34 | ✅ **Langsung** | K1, K2, K19, K20 | DIET + Confusion Matrix |
| 35 | ✅ **Langsung** | K1, K2, K10, K19 | DIET + 5-fold CV |
| 36 | ✅ **Langsung** | K1, K2, K5, K6, K19 | DIET + RegexFeaturizer + Lexical |
| 37 | ✅ **Langsung** | K1, K2, K4, K19 | DIET + berbagai embeddings |
| 38 | ✅ **Langsung** | K1, K2, K16 | Rasa NLU & Core foundational |
| 39 | ✅ **Langsung** | K1, K2, K3, K19 | DIET paper asli (sparse+dense) |
| 40 | ⬜ Latar belakang | K1 | Survey persepsi chatbot |
| 41 | ✅ **Langsung** | K1, K2, K8, K19 | Rasa + RAG + Multi-Stage Fallback |
| 42 | 🔶 Mendukung konsep | K4, K19 | BERT + SMOTE |
| 43 | 🔶 Mendukung konsep | K19 | Logistic Regression + SMOTE |
| 44 | 🔶 Mendukung konsep | K19 | TF-IDF + MNB + SMOTE |
| 45 | ✅ **Langsung** | K4, K18, K19 | IndoBERTweet, preprocessing minimal |

---

## Statistik Cakupan

| Kategori | Jumlah | Persentase |
|---|---|---|
| ✅ Langsung mendukung komponen | **27** | **60.0%** |
| 🔶 Mendukung konsep / paralel | **15** | **33.3%** |
| ⬜ Latar belakang saja | **3** | **6.7%** |
| **Total** | **45** | **100%** |

### Cakupan Per-Komponen Utama

| Komponen | Didukung oleh Jurnal No. | Total Jurnal |
|---|---|---|
| **K1 – Rasa Framework** | 4, 17, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 41 | **19** |
| **K2 – DIETClassifier** | 4, 17, 26, 27, 29, 31, 32, 33, 34, 35, 36, 37, 38, 39, 41 | **15** |
| **K4 – IndoBERT** | 3, 9, 11, 14, 18, 19, 20, 21, 22, 37, 42, 45 | **12** |
| **K10 – Cross-Validation** | 5, 11, 16, 35 | **4** |
| **K12 – Hyperparameter Tuning** | 6, 14, 15, 16, 27 | **5** |
| **K13 – Dropout/Regularization** | 12, 13, 14 | **3** |
| **K8 – FallbackClassifier** | 30, 41 | **2** |
| **K3 – CountVectorsFeaturizer** | 23, 30, 39 | **3** |
| **K5 – RegexFeaturizer** | 17, 36 | **2** |
| **K6 – LexicalSyntacticFeaturizer** | 36 | **1** |
| **K19 – Metrik F1/Precision/Recall** | 4–45 (hampir semua) | **42** |

---

## Analisis Gap: Apa yang Kurang / Perlu Diperhatikan?

### 1. Tidak Ada Jurnal Spesifik tentang Negation Handling (K14)

> [!IMPORTANT]
> Penelitian ini memiliki fitur unik berupa **8 pasang entity `.negated`** yang menjadi pembeda utama. Namun, tidak ada satupun dari 45 jurnal yang secara spesifik membahas *negation entity detection* di Rasa atau NLU framework lainnya. Ini sebenarnya **bukan kelemahan** — justru menjadi **novelty/kontribusi orisinal** penelitian. Namun, Anda perlu mengeksplisitkan ini di Bab 2 sebagai celah literatur (*research gap*) yang diisi oleh penelitian ini.

### 2. SMOTE/Oversampling vs Pendekatan yang Digunakan

> [!NOTE]
> Terdapat 8 jurnal (No. 5–8, 10, 42–44) yang membahas SMOTE/oversampling untuk data imbalanced, sementara penelitian ini **tidak** menggunakan SMOTE. Pendekatan penelitian ini adalah:
> - **Cross-validation** (K-Fold=5) untuk evaluasi yang lebih robust
> - **Dropout regularization** (0.2) untuk mencegah overfitting
> - **Hybrid featurizer** (IndoBERT + sparse features) untuk representasi yang lebih kaya
> 
> Ini perlu dijustifikasi di Bab 3/4 — mengapa Anda memilih pendekatan ini daripada augmentasi data.

### 3. RegexEntityExtractor (K7) Kurang Didukung Literatur

> [!NOTE]
> Penggunaan `RegexEntityExtractor` (TAv3, TAv4, TAv5) sebagai mekanisme rule-based fallback untuk entity recognition tidak banyak dibahas di jurnal rujukan. Hanya jurnal No. 36 (RASA 1) yang membahas `RegexFeaturizer` secara eksplisit. Komponen ini termasuk strategi teknis yang spesifik Rasa dan bisa dijustifikasi lewat dokumentasi resmi Rasa.

---

## Kesimpulan Akhir

> [!TIP]
> ### Verdik: **SUDAH CUKUP** ✅
> 
> Ke-45 jurnal rujukan **secara kolektif sudah mencakup dan mendukung** seluruh komponen utama yang diimplementasikan di `backend/rasa`. Rincian:
> 
> - **27 jurnal (60%)** secara langsung memakai komponen yang sama (Rasa, DIET, IndoBERT, dll.)
> - **15 jurnal (33.3%)** mendukung konsep-konsep paralel (cross-validation, hyperparameter tuning, regularization, handling imbalanced data)
> - **3 jurnal (6.7%)** berperan sebagai latar belakang riset chatbot
> - **Tidak ada jurnal yang bertentangan** dengan pendekatan yang diambil
> 
> ### Kekuatan Utama:
> 1. **19 jurnal Rasa-spesifik** — jumlah yang sangat solid untuk memvalidasi pemilihan framework
> 2. **12 jurnal IndoBERT** — kuat memvalidasi LanguageModelFeaturizer
> 3. **Paper asli DIET (No. 39)** dan **Rasa foundational (No. 38)** — referensi primer sudah ada
> 4. **Kombinasi sparse + dense features (TAv6)** terdukung oleh paper DIET asli (No. 39) yang justru merekomendasikan hal ini
> 
> ### Yang Perlu Ditegaskan di Skripsi:
> 1. Negation handling (`.negated` entity) sebagai **kontribusi orisinal** — belum ada di literatur
> 2. Justifikasi mengapa **tidak pakai SMOTE** meski banyak literatur yang merekomendasikan → jawab dengan: distribusi data cukup baik secara overall (850 kalimat), dan dropout + hybrid featurizer sudah cukup
> 3. Justifikasi `RegexEntityExtractor` cukup lewat **dokumentasi resmi Rasa** + hasil empiris di TAv3/TAv4/TAv5
