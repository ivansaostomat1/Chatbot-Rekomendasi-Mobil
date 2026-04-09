from pathlib import Path
import pandas as pd


# ======================================================
# PATH CONFIGURATION
# ======================================================

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


# ======================================================
# INTERNAL CSV LOADER
# ======================================================

def _load_csv(path: Path) -> pd.DataFrame:
    """
    Generic CSV loader dengan error handling
    """

    if not path.exists():
        raise FileNotFoundError(f"Dataset tidak ditemukan: {path}")

    try:
        df = pd.read_csv(path)

    except Exception as e:
        raise RuntimeError(f"Gagal membaca CSV: {path}\n{e}")

    if df.empty:
        raise ValueError(f"Dataset kosong: {path}")

    return df


# ======================================================
# DATASET LOADERS
# ======================================================

def load_mobil_dataset() -> pd.DataFrame:
    """
    Load dataset mobil utama
    """

    mobil_path = DATA_DIR / "mobil.csv"

    df = _load_csv(mobil_path)

    return df


def load_wholesales_dataset() -> pd.DataFrame:
    """
    Load dataset wholesales (ketersediaan unit di dealer / parts availability).
    Data per BRAND+MODEL+VARIAN -> indikator seberapa besar stok beredar.
    Tinggi = dealer banyak pesan = spare parts & jaringan servis lebih siap.
    """

    wholesales_path = DATA_DIR / "wholesales.csv"

    df = _load_csv(wholesales_path)

    return df


def load_retail_dataset() -> pd.DataFrame:
    """
    Load dataset retail (permintaan pasar aktual dari konsumen akhir).
    Data per BRAND (agregat bulanan) -> indikator popularitas brand di pasar.
    Tinggi = banyak dibeli konsumen = brand proven & dipercaya pasar.
    """

    retail_path = DATA_DIR / "retail.csv"

    df = _load_csv(retail_path)

    return df


# ======================================================
# MAIN DATA LOADER
# ======================================================

def load_all_datasets():
    """
    Load semua dataset yang diperlukan sistem.

    Returns: (mobil, wholesales, retail)
    - mobil     : spesifikasi kendaraan
    - wholesales: volume per varian  -> proxy ketersediaan parts & dealer network
    - retail    : volume per brand   -> proxy popularitas & permintaan pasar aktual
    """

    mobil = load_mobil_dataset()

    wholesales = load_wholesales_dataset()

    retail = load_retail_dataset()

    return mobil, wholesales, retail