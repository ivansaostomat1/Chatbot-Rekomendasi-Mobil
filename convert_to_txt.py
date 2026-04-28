"""
Skrip untuk menyalin seluruh file .py, .yml, .yaml, .ts, .tsx
dari proyek ke folder 'notebook' dengan ekstensi diubah menjadi .txt.
Struktur folder asli dipertahankan di dalam folder notebook.
"""

import os
import shutil

# Konfigurasi
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "notebook")

# Ekstensi yang akan di-convert
TARGET_EXTENSIONS = {".py", ".yml", ".yaml", ".ts", ".tsx"}

# Folder yang di-skip (tidak perlu disalin)
SKIP_DIRS = {
    "node_modules",
    ".next",
    "venv",
    "__pycache__",
    ".git",
    ".rasa",
    "notebook",       # hindari rekursi
    ".mypy_cache",
    ".pytest_cache",
    "dist",
    "build",
}


def main():
    # Bersihkan folder output jika sudah ada
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    file_count = 0

    for dirpath, dirnames, filenames in os.walk(PROJECT_ROOT):
        # Filter folder yang di-skip (in-place agar os.walk tidak masuk)
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

        for filename in filenames:
            _, ext = os.path.splitext(filename)
            if ext.lower() not in TARGET_EXTENSIONS:
                continue

            src_path = os.path.join(dirpath, filename)

            # Hitung path relatif dari root proyek
            rel_path = os.path.relpath(src_path, PROJECT_ROOT)

            # Ubah ekstensi menjadi .txt
            # Contoh: backend/app/main.py  ->  backend__app__main.py.txt
            # Atau pertahankan struktur folder:
            new_rel_path = rel_path + ".txt"

            dst_path = os.path.join(OUTPUT_DIR, new_rel_path)

            # Buat folder tujuan jika belum ada
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)

            # Salin file
            shutil.copy2(src_path, dst_path)
            file_count += 1
            print(f"  [OK] {rel_path}  ->  notebook/{new_rel_path}")

    print(f"\nSelesai! {file_count} file disalin ke folder 'notebook'.")


if __name__ == "__main__":
    main()
