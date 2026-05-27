import sys
from config import settings
from core.cleaner import RowCleanerEngine

def run_engine():
    print("="*50)
    print("🚀 TALATEE EMPTY ROW REMOVER ENGINE RUNNING...")
    print("="*50)

    # Contoh mencari file target di folder data/input
    # Anda bisa mengubah nama file sesuai dengan target market yang di-drop
    filename = "marketplace_data.csv"
    input_file = settings.INPUT_DIR / filename
    output_file = settings.OUTPUT_DIR / f"cleaned_{filename}"

    try:
        # Inisialisasi Engine
        engine = RowCleanerEngine(input_path=input_file, output_path=output_file)
        
        print(f"[INFO] Memproses file: {filename}...")
        metrics = engine.process()
        
        # Output Log Sukses
        print("\n" + "—"*40)
        print("🎯 PROCESS COMPLETION REPORT")
        print("—"*40)
        print(f"🔹 Total Data Awal   : {metrics['initial_rows']} baris")
        print(f"🔹 Baris Kosong Drop : {metrics['dropped_rows']} baris (CLEANED)")
        print(f"🔹 Total Data Bersih : {metrics['final_rows']} baris")
        print(f"📂 Saved to          : {output_file.name}")
        print("—"*40 + "\n")

    except FileNotFoundError as e:
        print(f"\n❌ [ERROR] {e}")
        print(f"💡 Silakan letakkan file CSV Anda di folder: {settings.INPUT_DIR} dengan nama '{filename}'\n")
    except Exception as e:
        print(f"\n❌ [FATAL SYSTEM ERROR] Terjadi kegagalan engine: {str(e)}\n")

if __name__ == "__main__":
    run_engine()