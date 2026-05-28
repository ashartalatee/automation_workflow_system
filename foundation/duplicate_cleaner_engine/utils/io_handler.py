import pandas as pd
import os

class IOHandler:
    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File tidak ditemukan di: {file_path}")
        
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            return pd.read_excel(file_path)
        else:
            raise ValueError("Format file tidak didukung! Gunakan CSV atau Excel.")

    @staticmethod
    def write_data(df: pd.DataFrame, file_path: str) -> None:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if file_path.endswith('.csv'):
            df.to_csv(file_path, index=False)
        elif file_path.endswith('.xlsx'):
            df.to_excel(file_path, index=False)
        print(f"[SUCCESS] Data bersih berhasil disimpan di: {file_path}")