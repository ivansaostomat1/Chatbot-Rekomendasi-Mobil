# 🚀 Cara Menjalankan Layanan (Daily Development)

Gunakan panduan ini untuk menyalakan sistem Otobot saat Anda mulai bekerja.

## ⚡ Cara Cepat (Khusus Windows)
Agar menghemat waktu, klik ganda file berikut di folder utama, atau jalankan perintah ini di CMD/Terminal:
```powershell

.\run_all.bat

```
Script tersebut otomatis membuka 4 terminal dan menyalakan semua sistem sekaligus.

---

## 🛠 Cara Manual (Mac / Linux / Windows)
Buka **4 Terminal** terpisah (atau gunakan fitur split panel di VS Code). Pastikan terminal Backend selalu mengaktifkan `venv`.

### Terminal 1: Frontend (UI)
```bash
cd frontend
npm run dev
```
*Layanan berjalan di: `http://localhost:3000`*

### Terminal 2: Backend (FastAPI & Ranking)
```bash
cd backend
# Aktifkan venv dulu (.\venv\Scripts\activate atau source venv/bin/activate)
uvicorn app.main:app --reload
```
*Layanan berjalan di: `http://localhost:8000`*

### Terminal 3: Rasa Core (NLP Server)
```bash
cd backend
# Aktifkan venv dulu
cd rasa
rasa run --enable-api --cors "*"
```
*Layanan berjalan di: `http://localhost:5005`*

### Terminal 4: Rasa Actions (Custom Logic)
```bash
cd backend
# Aktifkan venv dulu
cd rasa
rasa run actions
```
*Layanan berjalan di: `http://localhost:5055`*
