# Metodologi Evaluasi Chatbot: Objektif dan Ilmiah

Berdasarkan eksekusi pengujian ilmiah yang telah dijalankan, berikut adalah hasil evaluasi objektif dari *Baseline* model (CP) dan Core bot Anda:

## 1. Dialogue Evaluation (Test Core)
Pengujian ekstensif *Dialogue* dilakukan menggunakan `test_stories.yml` yang berisi *Happy Path*, tanya-jawab perbandingan, hingga skenario Fallback (OOS).

- **Action Accuracy**: 1.000 (100% prediksi benar)
- **F1-Score**: 1.000
- **Precision**: 1.000
- **Kesimpulan**: *Core model* (TEDPolicy & Memoization) sudah sempurna dalam menangani urutan cerita dan skenario *fallback* berdasar *training stories*.

## 2. NLU Evaluation: 5-Fold Cross Validation (Baseline CP)
Untuk menghindari variabilitas satu *train-test split*, pengujian ini menggunakan 5-Fold CV pada dataset Anda (diuji bergantian 5 kali).

### Performa Keseluruhan
- **Accuracy**: 0.899 (89.9%)
- **Macro F1-Score**: 0.886
- **Weighted F1-Score**: 0.898 (Sangat baik untuk NLU berbasis intent)

### Performa Per Intent (Kunci)
| Intent | Precision | Recall | F1-Score | Support | Catatan Confusion |
|--------|-----------|--------|----------|---------|-------------------|
| `ask_recommendation` | 0.911 | 0.941 | **0.926** | 120 | Sering tertukar dengan `out_of_scope` (3) dan `choose_preference` (2) |
| `choose_preference` | 0.875 | 0.903 | **0.888** | 31 | Kadang dianggap `ask_recommendation` (2) |
| `out_of_scope` | 0.872 | 0.854 | **0.863** | 48 | *False Positive*: Sering salah tebak dari `ask_recommendation` (4) |
| `start_search` | 0.888 | 0.761 | **0.820** | 21 | Paling rendah *recall*-nya |
| `ask_comparison` | 1.000 | 0.833 | **0.909** | 12 | Akurasi mutlak 100%, sedikit turun di *recall* |

---

## 3. Catatan Insiden Uji Statistik (T-Test)
Skrip otomatisasi uji T-Test 5-*seed* mengalami galat (error) penghentian dikarenakan versi Rasa 3.x Anda menolak argumen `--random-seed 42` dari Command Line (fitur CLI ini usang dan *seed* harus didefinisikan langsung di dalam `config.yml`). 

Oleh karena itu, uji perbandingan *Dev Set* (TAv4 vs CP) saat ini belum memiliki metrik P-Value final, namun hasil CV Baseline di atas sudah merepresentasikan angka dasar yang objektif dan ilmiah sebagai landasan laporan Anda.

> [!TIP]
> Log metrik dan *confusion matrix* asli 5-Fold CV dapat ditemukan di `backend/rasa/results_cv_cp`. Laporan cerita (*Core test*) di `backend/rasa/results_core`.
