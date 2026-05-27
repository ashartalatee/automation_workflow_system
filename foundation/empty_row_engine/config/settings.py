import os
from pathlib import Path

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data Paths
INPUT_DIR = BASE_DIR / "data" / "input"
OUTPUT_DIR = BASE_DIR / "data" / "output"

# Pastikan folder data eksis
INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Engine Configurations
# 'how="all"' artinya baris hanya dihapus jika SEMUA kolom bernilai null/kosong
DROPNA_STRATEGY = "all"