# Alur Sistem: Dari Data Mentah Menjadi Rekomendasi (Studi Kasus Nyata)

Dokumen ini menjelaskan alur **praktis** (bukan hanya teori matematis) tentang bagaimana data dari sebuah brosur spesifikasi mobil yang mentah diproses setahap demi setahap hingga menjadi peringkat teratas di layar aplikasi Anda.

Mari kita asumsikan kasus: Pengguna mencari **"Carikan saya mobil untuk keluarga yang nyaman di harga 300 jutaan."**

Dan di dalam database, kita memiliki satu data mentah mobil: **Toyota Kijang Innova Zenix 2.0 G CVT** seharga **430 juta**. Bagaimana Innova ini beradu dengan mobil lain? Berikut adalah perjalanannya.

---

## TAHAP 1: Pipeline Feature Engineering (Penyiapan Data)

Saat backend pertama kali menyala, seluruh 612 mobil dalam database `.csv` mentah dimasukkan ke dalam memori. File yang mengatur tahap ini adalah `backend/app/feature_engineering/pipeline.py`.

### Langkah 1: Pembersihan Numerik (`clean_numeric_columns`)
Data dari brosur sangat tidak beraturan.
- **Data Mentah**: Kolom `CC` berisi `"1.987 cc"`, Harga berisi `"Rp 430.000.000"`.
- **Proses**: Sistem menghapus string dan menjadikannya angka mentah (integer/float) agar bisa dihitung komputernya.
- **Hasil**: `CC` = `1987`, `HARGAOTR` = `430000000`.

### Langkah 2: Encoding Fitur Kategorikal (`encode_granular_features`)
Banyak fitur keselamatan dan kenyamanan dalam bentuk teks.
- **Data Mentah**: Kolom `LEATHER_SEAT` (Jok Kulit) berisi teks `"Kulit Sintetis"`.
- **Proses**: Sistem mengubah tipe jok menjadi level angka. (Contoh: Tidak ada = 0, Daur Ulang = 1, Kulit Sintetis = 2, Kulit Asli = 3, Nappa = 4).
- **Hasil**: `LEATHER_SEAT_ENCODED` = `2`.

### Langkah 3: Integrasi Data Eksternal (Wholesales & Retail GAIKINDO)
Sistem tidak hanya melihat spesifikasi mesin, tetapi juga prospek *market share* agar pengguna tidak direkomendasikan mobil yang sebentar lagi akan di *discontinue* (suntik mati).
- **Proses**: Sistem mengambil data pergerakan pabrik (*wholesale*) untuk membandingkan jumlah pasokan kuartal akhir tahun dibandingkan kuartal awal, lalu menghitung proporsi peredaran mobil di jalan (*retail*).
- **Hasil**: Sistem menyematkan nilai `LIFECYCLE_SCORE` (Kesehatan umur tipe mobil) dan `BRAND_STRENGTH_SCORE` (Kekuatan ekosistem komunitas / layanan purna jual dari pabrikan, misal Toyota memiliki skor yang sangat tinggi).

### Langkah 4: Pembuatan Fitur Turunan (`add_derived_features`)
Sistem menciptakan fitur baru yang tidak tertulis di brosur tapi sangat penting dalam dunia nyata.
- **Proses**: Sistem mengambil angka `HORSE POWER` dan membaginya dengan `WEIGHT (GVW)`.
- **Hasil**: Tercipta metrik *Power-to-Weight Ratio* (PWR) dan *Torque-to-Weight Ratio* (TWR). Ini krusial karena mesin 200HP pada mobil 3 Ton akan terasa lebih lemot daripada mesin 100HP pada mobil 1 Ton.

### Langkah 5: Kalkulasi Indeks Akhir (`calculate_indices`)
Sistem meringkas puluhan fitur menjadi 12 **Pilar INDEX** utama berskala `1` hingga `10`.
- **Proses**: Seluruh mobil dirata-ratakan menggunakan *Z-Score*. Misalnya, Innova Zenix memiliki Wheelbase panjang (2850mm), Kapasitas Kursi 7, dan Bagasi cukup besar. Fitur-fitur ini dikelompokkan dan dibandingkan rata-ratanya dengan mobil-mobil sempit seperti Agya.
- **Hasil**: Zenix mungkin mendapat skor **INDEX_SPACE = 8.5/10**. Begitu juga untuk fitur lain seperti **INDEX_SAFETY = 6.2/10** (Tergantung kelengkapan sensor yang dimilikinya).

Selesai di tahap ini, spesifikasi teks mentah Innova telah berubah menjadi matriks angka murni yang siap dilombakan.

---

## TAHAP 2: Pemrosesan Kalimat oleh RASA (NLP)

Pengguna mengetik: **"Carikan mobil untuk keluarga yang nyaman di harga 300 jutaan."**

1.  **Ekstraksi Leksikon**: Model membedah kalimat tersebut menjadi dua frasa penting: `"keluarga"` dan `"nyaman"`. Dan memotong `300 jutaan` sebagai filter uang absolut (Maks. Budget = Rp 399.999.999).
2.  **Pemetaan Kebutuhan (Semantic Mapping)**: Kata `"keluarga"` dan `"nyaman"` dikonversi lewat tabel ontologi backend menjadi pilar kebutuhan profil: **"Family Comfort"**.

---

## TAHAP 3: Penetapan Bobot (AHP / Analytic Hierarchy Process)

Sekarang sistem harus menerjemahkan profil "Family Comfort" ke dalam porsi prioritas untuk algoritma mencari kandidat. Profil "Family Comfort" ini sudah dievaluasi sebelumnya (disimpan dalam *knowledge base*).

Dalam perhitungan *Pairwise Comparison* sistem (AHP):
- Untuk profil "Family Comfort", algoritma disuruh untuk menganggap `INDEX_SPACE` dan `INDEX_PASSENGER_COMFORT` jauh lebih berharga ketimbang `INDEX_POWER` atau `INDEX_HANDLING`.
- Sistem lalu mengeluarkan distribusi persentase akhir (Bobot):
  - Kriteria *Space* mendapat 18%.
  - Kriteria *Passenger Comfort* mendapat 17%.
  - Kriteria *Safety* mendapat 15%.
  - Sementara Kriteria *Handling* (sportivitas) hanya mendapat 3%.

Inilah kacamata (perspektif) yang akan digunakan algoritma untuk menilai seluruh mobil di database.

---

## TAHAP 4: Pertarungan Kandidat (VIKOR Ranking Engine)

Seluruh data matriks mobil akan dimasukkan ke algoritma perangkingan **VIKOR** (`backend/vikor/ranking_engine.py`) dengan aturan main berikut:

### Langkah 1: Eliminasi Hard Constraints
Syarat harga pengguna maksimal Rp 399.999.999.
- **Proses**: Sistem melihat harga Innova Zenix tipe G (Rp 430.000.000). Karena melebihi batas mutlak pengguna (Filter Harga), Zenix **LANGSUNG DIELIMINASI** dan tidak ikut masuk perankingan, meskipun skor *Space* dan nyamannya sangat tinggi.
- Mobil-mobil yang lolos masuk arena hanyalah mobil-mobil yang harganya di bawah 400 Juta, misalnya: **Toyota Avanza Veloz**, **Hyundai Stargazer**, **Suzuki Ertiga**, dan **Mitsubishi Xpander**.

### Langkah 2: Mencari Jarak ke Mobil "Imanjiner" Paling Sempurna (Utility & Regret)
Di antara kandidat yang tersisa, VIKOR membuat satu *baseline* mobil impian (Semua speknya paling tinggi) dan mobil terburuk (Semua speknya terendah).

Untuk tiap mobil (Misalnya **Hyundai Stargazer**):
- **Nilai Kepuasan (Utility / S)**: Stargazer diukur kelengkapannya. Berapa banyak kekurangannya dibandingkan mobil Sempurna pada semua kriteria (dikalikan dengan bobot 18% untuk Space, dll). Semakin kecil jaraknya ke mobil sempurna, nilainya semakin baik.
- **Nilai Komplain Utama (Regret / R)**: Stargazer dinilai: "Apa sih kelemahan terburuk mobil ini?". Hal ini untuk mencegah merekomendasikan mobil yang kabinnya super luas, tapi keselamatannya nol besar. 

### Langkah 3: Penentuan Pemenang (Nilai Q)
VIKOR menggabungkan skor `S` dan `R` untuk menghasilkan nilai kesimpulan **Q**. Mobil dengan skor $Q$ terendah (Paling minim kompromi dan kekurangan) akan didorong ke peringkat #1.
Misalnya, **Hyundai Stargazer** mungkin memenangkan peringkat 1 atas Xpander, karena secara keseimbangan metrik ADAS (Safety) dan keluasan baris ketiganya sedikit memunggungi Xpander dalam simulasi *Z-Score* linear dan bobot "Family Comfort".

### Langkah 4: Penyampaian Rekomendasi
Sistem mengirimkan peringkat (Stargazer #1, Veloz #2, Xpander #3) kembali ke RASA, dan RASA merangkainya dalam teks natural untuk ditampilkan ke layar obrolan (*frontend*) pengguna.
