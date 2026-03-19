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
    Load dataset wholesales (popularitas)
    """

    wholesales_path = DATA_DIR / "wholesales.csv"

    df = _load_csv(wholesales_path)

    return df


# ======================================================
# MAIN DATA LOADER
# ======================================================

def load_all_datasets():
    """
    Load semua dataset yang diperlukan sistem
    """

    mobil = load_mobil_dataset()

    wholesales = load_wholesales_dataset()

    return mobil, wholesales