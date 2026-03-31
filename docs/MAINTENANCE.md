# 🛠 Maintenance & Troubleshooting

Gunakan panduan ini saat Anda perlu mengubah data model chatbot, jika ada masalah port, atau jika menemukan error teknis.

## 📈 Melatih Ulang Chatbot (Re-Train)
Jika Anda mengubah file di folder `rasa/data/` atau `domain.yml`, jalankan:
```bash
cd backend/rasa
rasa train
```
Setelah selesai, restart Terminal 3 & 4 (Rasa Core & Rasa Actions).

## 🛑 Cara Mematikan Port (Windows)
Jika Anda tidak sengaja menutup terminal tanpa mematikan server, jalankan perintah ini di CMD/Powershell:
```bash
# Ganti 8000 dengan nomor port yang bermasalah (3000, 8000, 5005, 5055)
netstat -ano | findstr :8000

# Copy angka PID dari hasil pencarian di atas, lalu jalankan:
taskkill /F /PID <ANGKA_PID>
```

## 🔍 Diagnosis Sering Terjadi
- **"Rasa not found"**: Pastikan Anda sudah menjalankan perintah `activate` pada `venv` (`.\venv\Scripts\activate`) di setiap terminal backend yang baru dibuka.
- **Port already in use**: Sering terjadi jika Anda tidak sengaja menutup layar terminal saat sistem masih menyala. Gunakan langkah "Mematikan Port" di atas.
- **Model not loading**: Pastikan Anda sudah melatih model chatbot menggunakan `rasa train` dan ada file model di folder `backend/rasa/models/`.
