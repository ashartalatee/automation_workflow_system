from utils.io_handler import IOHandler
from core.strategies import DuplicateStrategy

class DuplicateCleanerEngine:
    def __init__(self, config: dict):
        self.config = config

    def run(self):
        print("[START] Menjalankan Duplicate Cleaner Engine...")
        
        # 1. Load Data
        df = IOHandler.read_data(self.config["input_file"])
        print(f"[INFO] Data berhasil dimuat. Total baris awal: {len(df)}")

        # 2. Tentukan Kolom Target Berdasarkan Strategi
        target_cols = DuplicateStrategy.resolve_columns(
            strategy_type=self.config["strategy"],
            custom_cols=self.config.get("target_columns")
        )

        # 3. Eksekusi Pembersihan
        df_clean = DuplicateStrategy.clean(df, subset_columns=target_cols)
        print(f"[INFO] Pembersihan selesai. Total baris akhir: {len(df_clean)}")

        # 4. Simpan Data
        IOHandler.write_data(df_clean, self.config["output_file"])
        print("[FINISHED] Proses pembersihan selesai dengan aman.\n")