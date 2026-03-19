# Cheatsheet & Command Development

File ini merupakan daftar perintah (*commands*) yang sering digunakan saat mengembangkan (development) aplikasi Chatbot Rekomendasi Mobil ini. 
Daripada menghafal, kamu bisa cukup **copy-paste** perintah-perintah di bawah ini ke terminalmu.

---

## 1. Menjalankan Frontend (Next.js)
Gunakan perintah ini untuk menyalakan User Interface (UI).
```bash
cd frontend
npm run dev
```

---

## 2. Mengaktifkan Virtual Environment (Backend)
**PENTING**: Sebelum menjalankan Backend (FastAPI) atau Rasa NLP, kamu harus mengaktifkan virtual environment terlebih dahulu agar komputer menggunakan library Python khusus untuk proyek ini.
```bash
cd backend
.\venv\Scripts\activate
```

---

## 3. Menjalankan Backend API (FastAPI)
Setelah virtual environment aktif, jalankan sistem ranking VIKOR (pastikan posisimu ada di dalam folder `backend`, **bukan** di `backend/rasa`).
```bash
uvicorn app.main:app --reload
```

---

## 4. Perintah-perintah RASA (NLP & Actions)

Pastikan kamu berada di folder `backend/rasa` (`cd backend/rasa`) dengan virtual environment yang sudah aktif.

**Menyalakan Rasa API Server (Port 5005)**
```bash
rasa run --enable-api --cors "*"
```

**Menyalakan Rasa Action Server (Port 5055)**
*(Dibutuhkan untuk memproses custom python code, menghubungkan user ke FastAPI)*
```bash
rasa run actions
```

**Melatih Ulang (Train) Model Rasa**
*(Jalankan jika kamu baru saja mengubah domain.yml atau data NLU)*
```bash
rasa train
```

**Mengecek dan Debug NLP Mode Shell**
*(Menjalankan chatbot hanya di terminal, melihat probabilitas klasifikasi intent & entity)*
```bash
rasa shell
# atau untuk melihat log debug error:
rasa shell --debug
```

---

## 5. Perintah Darurat (Kill Port)

Jika terminal error karena *"Port is already in use"* (Port bentrok/nyangkut di background), gunakan perintah Windows ini:

**Mengecek Proses yang memakai Port NodeJS (Misal 3000):**
```bash
netstat -ano | findstr :3000
```
**Mematikan paksa (Kill) server Node.js:**
```bash
taskkill /F /IM node.exe
```

**Mengecek Proses yang memakai Port Action Server (5055):**
```bash
netstat -ano | findstr :5055
```
