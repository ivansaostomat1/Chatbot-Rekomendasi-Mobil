# 🎓 Panduan Instalasi & Menjalankan Otobot (Tutor.md)

Panduan ini berisi tahapan lengkap, dari cara melakukan *clone* proyek di *device* / laptop baru, hingga menyesuaikan perintah jika kamu menggunakan OS yang berbeda (Windows vs MacOS/Linux).

---

## 1. Persiapan Awal (Pindah Device / Laptop Baru)

Jika kamu berpindah ke laptop baru, pastikan laptop tersebut telah terinstal:
- **Git**
- **Node.js** (Disarankan versi 18 atau 20 LTS)
- **Python** (Disarankan versi 3.9 atau 3.10)

### Clone Repository (Hanya dilakukan 1x di device baru)
Buka terminal/CMD/Powershell dan jalankan:
```bash
git clone https://github.com/ivansaostomat1/Chatbot-Rekomendasi-Mobil.git
cd Chatbot-Rekomendasi-Mobil
```

---

## 2. Menginstal Dependency (Library) di Device Baru

Karena folder `node_modules` (frontend) dan `venv` (backend) sudah kita blokir dari GitHub agar ringan, kamu **wajib menginstalnya kembali** di laptop baru satu per satu.

### A. Frontend (Javascript / Next.js)
**Berlaku sama untuk semua OS (Windows / Mac / Linux):**
```bash
cd frontend
npm install
```

### B. Backend (Python / FastAPI / Rasa)
Kamu harus membuat wadah *virtual environment* (`venv`) yang baru di komputermu, lalu mengunduh library dari `requirements.txt`. Pastikan terminal utama sejajar di dalam folder `backend/`.

**Untuk Windows:**
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

**Untuk MacOS / Linux:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

*(Catatan: Langkah 2A dan 2B di atas hanya perlu dilakukan sekali ketika baru pindah laptop atau ketika ada update package baru).*

---

## 3. Cara Menjalankan Layanan (Daily Development)

Setiap kali kamu mau mengerjakan skripsi atau mendemonstrasikan sistem ini secara lokal, kamu harus membuka **4 Terminal** (usahakan di-*split* panel terminalnya agar rapi).

### Terminal 1: Menyalakan UI (Frontend Next.js)
Berlaku untuk semua OS:
```bash
cd frontend
npm run dev
```

### Terminal 2: Menyalakan API & Sistem Ranking (FastAPI)
Jika terminal baru dibuka, pastikan kamu selalu MENGAKTIFKAN `venv` terlebih dahulu.

**Windows:**
```bash
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --reload
```
**MacOS / Linux:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### Terminal 3 & 4: Menyalakan Chatbot NLP (Rasa)
Rasa membutuhkan 2 terminal/server sekaligus agar bisa menerima logika dari Python Actions dan memproses teks klasifikasi.

**Terminal 3 (Menyalakan AI Core):**
*Windows:*
```bash
cd backend/rasa
.\venv\Scripts\activate
rasa run --enable-api --cors "*"
```
*MacOS / Linux:*
```bash
cd backend/rasa
source ../venv/bin/activate
rasa run --enable-api --cors "*"
```

**Terminal 4 (Menyalakan Custom Actions Server):**
*Windows:*
```bash
cd backend/rasa
.\venv\Scripts\activate
rasa run actions
```
*MacOS / Linux:*
```bash
cd backend/rasa
source ../venv/bin/activate
rasa run actions
```

---

## 4. Tips & Trik Darurat

### Gagal Menyalakan Server (Port Already in Use)
Jika sewaktu-waktu terminal gagal dinyalakan karena pesan error *"port is already in use"*, artinya ada server lama yang belum sepenuhnya tertutup ('nyangkut' di *background* proses laptopmu).

**Di Windows:**
Cek port yang tersangkut (contoh jika port API 8000 yang error):
```bash
netstat -ano | findstr :8000
```
Lalu matikan paksa dengan angka PID (angka paling ujung kanan dari output di atas):
```bash
taskkill /F /PID <masukkan_angka_pid>
```

**Di MacOS / Linux:**
```bash
lsof -i :8000
kill -9 <masukkan_angka_pid>
```

### Melatih Ulang Chatbot (Re-Train Model)
Apabila kamu mengubah data kalimat sapaan, contoh mobil, atau respons bot di file `nlu.yml` / `stories.yml` / `domain.yml`, kamu wajib melatih otak (model) si chatbot kembali agar ia mengerti:
```bash
# Pastikan terminal ada di folder backend/rasa dan venv sedang menyala
rasa train
```
Setelah proses *training* selesai, matikan Terminal 3 & 4 (`Ctrl + C`), lalu hidupkan kembali keduanya.
