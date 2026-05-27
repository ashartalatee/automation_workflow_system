import pandas as pd
from pathlib import Path
from config.settings import DROPNA_STRATEGY

class RowCleanerEngine:
    def __init__(self, input_path: Path, output_path: Path):
        self.input_path = input_path
        self.output_path = output_path

    def process(self) -> dict:
        """
        Membaca, menghitung baris kosong, membersihkan, dan menyimpan data.
        """
        if not self.input_path.exists():
            raise FileNotFoundError(f"File input tidak ditemukan di: {self.input_path}")

        # 1. Load Data
        df = pd.read_csv(self.input_path)
        initial_rows = len(df)

        # 2. Cleaning Logic
        # Hapus baris yang benar-benar kosong secara sistem (NaN/Null)
        df_cleaned = df.dropna(how=DROPNA_STRATEGY)
        
        # PERBAIKAN: Ubah spasi gaib (" ") menjadi NaN terlebih dahulu di semua kolom
        df_cleaned = df_cleaned.replace(r'^\s*$', pd.NA, regex=True)
        df_cleaned = df_cleaned.dropna(how=DROPNA_STRATEGY)
        
        final_rows = len(df_cleaned)
        dropped_rows = initial_rows - final_rows

        # 3. Export Data
        df_cleaned.to_csv(self.output_path, index=False)

        return {
            "status": "SUCCESS",
            "initial_rows": initial_rows,
            "final_rows": final_rows,
            "dropped_rows": dropped_rows
        }