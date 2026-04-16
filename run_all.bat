@echo off
echo ==================================================
echo   Menjalankan Otobot (Frontend, API, dan NLP)
echo ==================================================

echo [1/4] Memulai Next.js Frontend (UI)...
start cmd /k "title Frontend (UI) && cd frontend && npm run dev"

echo [2/4] Memulai FastAPI Backend (API ^& Ranking)...
start cmd /k "title FastAPI (Backend) && cd backend && call venv\Scripts\activate && uvicorn app.main:app --reload"

set "train=n"
set /p "train=Apakah Anda ingin melatih ulang (train) Rasa model? (y/n): "
if /i "%train%"=="y" (
    echo [0/4] Melatih model Rasa... (Mohon tunggu)
    cd backend\rasa && call ..\venv\Scripts\activate && rasa train && cd ..\..
)

echo [3/4] Memulai Rasa Core (NLP Server)...
start cmd /k "title Rasa Core (NLP) && cd backend\rasa && call ..\venv\Scripts\activate && rasa run --enable-api --cors ""*"""

echo [4/4] Memulai Rasa Actions (Custom Logic)...
start cmd /k "title Rasa Actions (Logic) && cd backend\rasa && call ..\venv\Scripts\activate && rasa run actions --auto-reload"

echo.
echo Semua layanan sedang dinyalakan di terminal terpisah!
echo - Frontend UI : http://localhost:3000
echo - FastAPI     : http://localhost:8000
echo - Rasa Core   : http://localhost:5005
echo - Rasa Actions: http://localhost:5055
echo.
echo Biarkan terminal-terminal tersebut tetap terbuka selama pengerjaan.
pause
