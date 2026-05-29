import os
import pandas as pd
from src.engine import ColumnStandardizerEngine

def main():
    # Define path folder input dan output secara jelas
    RAW_DATA_DIR = os.path.join("data", "raw")
    CLEAN_DATA_DIR = os.path.join("data", "clean")
    
    input_filename = "marketplaces_raw.csv"
    output_filename = "marketplaces_clean.csv"
    
    path_input = os.path.join(RAW_DATA_DIR, input_filename)
    path_output = os.path.join(CLEAN_DATA_DIR, output_filename)

    # 1. Validasi: Pastikan file inputnya ada sebelum diproses
    if not os.path.exists(path_input):
        print(f"[ERROR] File mentah tidak ditemukan di: {path_input}")
        print("Silakan buat folder 'data/raw/' dan letakkan file CSV Anda di sana.")
        return

    print(f"[INFO] Membaca data mentah dari: {path_input}")
    df_raw = pd.read_csv(path_input)
    
    print("\n=== KOLOM SEBELUM STANDARISASI ===")
    print(df_raw.columns.tolist())
    print("-" * 50)

    # 2. Jalankan Proses Standarisasi Kolom
    engine = ColumnStandardizerEngine()
    df_clean = engine.process(df_raw)
    
    print("\n=== KOLOM SESUDAH STANDARISASI ===")
    print(df_clean.columns.tolist())
    print("-" * 50)

    # 3. Validasi & Simpan: Pastikan folder output ada, lalu simpan datanya
    if not os.path.exists(CLEAN_DATA_DIR):
        os.makedirs(CLEAN_DATA_DIR) # Buat folder otomatis jika belum ada
        
    df_clean.to_csv(path_output, index=False)
    print(f"\n[SUCCESS] Data berhasil distandarisasi dan disimpan di: {path_output}")

if __name__ == "__main__":
    main()