# 🎓 Panduan Instalasi & Menjalankan Otobot

Panduan ini berisi tahapan lengkap, dari cara melakukan *clone* proyek di *device* / laptop baru, hingga menyesuaikan perintah jika kamu menggunakan OS yang berbeda (Windows vs MacOS/Linux).

---

## 1. Persiapan Awal (Pindah Device / Laptop Baru)

Jika kamu berpindah ke laptop baru, pastikan laptop tersebut telah terinstal Software berikut:
- **Git**: [Unduh di sini](https://git-scm.com/)
- **Node.js**: Versi 18, 20 LTS, atau lebih baru. [Unduh di sini](https://nodejs.org/)
- **Python**: **Sangat Disarankan versi 3.10 hingga 3.14**. (Versi saat ini di pengembangan: 3.14.0). [Unduh di sini](https://www.python.org/)

### Clone Repository (Hanya dilakukan 1x di device baru)
Buka terminal/CMD/Powershell dan jalankan:
```bash
git clone https://github.com/ivansaostomat1/Chatbot-Rekomendasi-Mobil.git
cd Chatbot-Rekomendasi-Mobil
```

---

## 2. Menginstal Dependency (Library)

Karena folder `node_modules` (frontend) dan `venv` (backend) tidak diunggah ke GitHub, kamu **wajib menginstalnya kembali** di laptop baru.

### A. Frontend (Next.js)
```bash
cd frontend
npm install
```

### B. Backend (Python / FastAPI / Rasa)
Pastikan kamu berada di folder `backend/` untuk membuat *virtual environment* (`venv`).

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

> [!TIP]
> `requirements.txt` sudah dikunci (pinned) versinya agar sistem tetap stabil meskipun kamu berpindah perangkat.

---

## 3. Cara Menjalankan Layanan (Daily Development)

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

---

## 4. Tips & Troubleshooting

### Port yang Digunakan
Sistem ini menggunakan beberapa port utama. Jika ada error "Port already in use", cek port berikut:
- **3000**: UI (Next.js)
- **8000**: API (FastAPI)
- **5005**: NLP (Rasa Core)
- **5055**: Logic (Rasa Actions)

### Cara Mematikan Port (Windows)
Jika terminal tertutup tapi server masih 'nyangkut':
```bash
# Ganti 8000 dengan port yang bermasalah
netstat -ano | findstr :8000
taskkill /F /PID <ANGKA_PID_DARI_HASIL_DI_ATAS>
```

### Melatih Ulang Chatbot (Re-Train)
Jika kamu mengubah file di folder `rasa/data/` atau `domain.yml`, jalankan:
```bash
cd backend/rasa
rasa train
```
Setelah selesai, restart Terminal 3 & 4.

### Error "Rasa not found"
Pastikan kamu sudah menjalankan perintah `activate` pada `venv` di setiap terminal backend yang baru dibuka.

