# 💿 Panduan Instalasi & Persiapan Awal

Panduan ini berisi cara melakukan *clone* proyek di *device* / laptop baru, menginstal perangkat lunak yang dibutuhkan, hingga mengunduh library yang hilang.

## 1. Persiapan Awal (Pindah Laptop Baru)

Pastikan laptop Anda telah terinstal Software berikut:

- **Git**: [Unduh di sini](https://git-scm.com/)
- **Node.js**: Versi 18, 20 LTS, atau lebih baru. [Unduh di sini](https://nodejs.org/)
- **Python**: **Sangat Disarankan versi 3.10 hingga 3.14**. [Unduh di sini](https://www.python.org/)

### Clone Repository (Hanya dilakukan 1x)

Buka terminal/CMD/Powershell dan jalankan:

```bash
git clone https://github.com/ivansaostomat1/Chatbot-Rekomendasi-Mobil.git
cd Chatbot-Rekomendasi-Mobil
```

## 2. Menginstal Dependency (Library)

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
