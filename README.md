# 🚗 Otobot - Sistem Rekomendasi Mobil Cerdas (NLP + VIKOR)

**Otobot** adalah sebuah sistem chatbot *hybrid* dua arah yang dirancang untuk merekomendasikan mobil terbaik berdasarkan kebutuhan dan preferensi pengguna. Sistem ini menggabungkan pemrosesan bahasa alami (**Natural Language Processing / NLP**) dengan sistem pendukung keputusan (**Multi-Criteria Decision Making / MCDM**) untuk menghasilkan peringkat mobil yang transparan secara ilmiah.

Proyek ini dibangun sebagai tugas akhir (Capstone/Skripsi) dengan fokus pada penggabungan teknik NLP (Rasa) dan metode matematika **VIKOR** (VlseKriterijumska Optimizacija I Kompromisno Resenje) untuk memodelkan solusi kompromi terbaik bagi pembeli mobil.

---

## ✨ Fitur Utama

1. **Natural Language Understanding (NLU)**
   - Mendeteksi *Intent* dan *Entity* dari bahasa gaul/sehari-hari (misal: *"cari mobil irit buat keluarga under 300 juta yang ada sunroof"*).
   - Di-training menggunakan **DIETClassifier** dari framework Rasa.

2. **Dua Fase Filtering (Hard & Soft Criteria)**
   - **Fase 1 (Clustering & Constraints):** Menyaring mobil berdasarkan syarat mutlak (budget, jumlah kursi, sunroof) dan mengelompokkan mobil ke dalam *Cluster* (City Car, Family Car, SUV/Offroad, dll).
   - **Fase 2 (VIKOR Ranking):** Menghitung nilai kompromi (S, R, Q) pada mobil kandidat berdasarkan Multi-Kriteria (Performa, Efisiensi, Kenyamanan, Keamanan, dll).

3. **Smart Weighting (Pure User-Driven)**
   - Pipeline bobot yang sangat fleksibel: NLP menyarankan *slider* berdasarkan kata kunci pengguna, lalu pengguna dapat mengatur manual 12 dimensi skor (0-10) untuk mempersonalisasi hasil akhir.

4. **Transparansi Akademis (Scientific Breakdown)**
   - Setiap kartu rekomendasi mobil memiliki tombol untuk membongkar perhitungan *backend*:
     - **📊 INDEX:** Breakdown multi-kriteria untuk melihat keunggulan tiap mobil.
     - **🧠 NLP:** Validasi pipeline ekstraksi entitas dan pengujian tingkat akurasi pemetaan kata.
     - **🏆 VIKOR:** Visualisasi perhitungan kompromi matematis ($Q_2 - Q_1 \ge DQ$) dan analisis sensitivitas beban (Sensitivity Analysis).
     - **📎 Clustering:** Validasi semantik dari fitur yang melekat pada grup tipe mobil serta perhitungan skor Silhouette.

---

## 🏗️ Arsitektur Teknologi

Aplikasi ini menggunakan teknologi modern dan didesain berbasis *microservices*:

- **🌐 Frontend:** [Next.js](https://nextjs.org/) (React, TypeScript, CSS Modules)
- **⚙️ Backend API:** [FastAPI](https://fastapi.tiangolo.com/) (Python, Pandas, Scikit-Learn)
- **🧠 AI / NLP:** [Rasa Open Source](https://rasa.com/) (Rasa Core & Rasa Action Server)

---

## 📘 Panduan Pengoperasian

Untuk memudahkan pencarian, dokumentasi telah dipecah menjadi beberapa bagian:

1.  **[🚀 Cara Menjalankan Bot (Daily)](docs/RUN.md)** - Buka ini setiap hari untuk menyalakan sistem.
2.  **[💿 Instalasi & Setup Awal](docs/INSTALL.md)** - Gunakan ini jika Anda baru melakukan *clone* atau pindah laptop.
3.  **[🛠 Maintenance & Tuning](docs/MAINTENANCE.md)** - Panduan melatih ulang model (*re-train*) dan perbaikan *error*.

---

## ⚡ Quick Start (Windows)
Jika Anda sudah melakukan instalasi, cukup jalankan perintah berikut di terminal utama:
```powershell
.\run_all.bat
```
Script ini akan membuka semua terminal yang dibutuhkan secara otomatis.

---

## 📂 Struktur Direktori Utama

```
📁 Chatbot-Rekomendasi-Mobil
├── 📁 backend                   # Logic perhitungan dan API Server Utama
│   ├── 📁 app                   # FastAPI Routes & VIKOR Engine integration
│   ├── 📁 data                  # Database CSV (mobil.csv, wholesales.csv)
│   ├── 📁 rasa                  # Model NLP, Intents, dan NLP Pipeline
│   │   ├── 📁 actions           # Script sinkronisasi Rasa ke FastAPI 
│   │   └── config.yml           # Konfigurasi DIETClassifier
│   ├── 📁 vikor                 # Algoritma Matematika MCDM 
│   └── requirements.txt         # Daftar dependency backend
├── 📁 frontend                  # User Interface
│   ├── 📁 public                # Gambar dan desain UI statis
│   ├── 📁 src
│   │   ├── 📁 app               # Next.js 14 App Router
│   │   └── 📁 components        # Komponen React (CarCard, Modal Evaluasi, Sidebar)
│   ├── package.json
│   └── next.config.ts
└── README.md                    # Dokumentasi ini
```

---
*Dikembangkan untuk eksperimen Skripsi / Capstone Project: Otobot Car Recommender System.*
