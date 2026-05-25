import os
from src.config_loader import load_config
from src.file_scanner import scan_input_files
from src.name_generator import generate_rename_map
from src.writer_engine import execute_rename

def main():
    # Definisikan Workspace
    INPUT_DIR = "data/input"
    OUTPUT_DIR = "data/output"
    
    try:
        # 1. Load Aturan
        config = load_config()
        
        # 2. Scan Target File
        input_files = scan_input_files(INPUT_DIR, config["target_extension"])
        if not input_files:
            print(f"Tidak ada file dengan ekstensi {config['target_extension']} di folder '{INPUT_DIR}'")
            return
            
        # 3. Kalkulasi & Validasi Struktur Nama Baru (Tanpa menyentuh file fisis)
        rename_tasks = generate_rename_map(input_files, config)
        
        # 4. Eksekusi Perubahan Fisis (Single Writer)
        execute_rename(rename_tasks, INPUT_DIR, OUTPUT_DIR)
        
    except Exception as e:
        print(f"ENGINE CRASH / HALTED: {str(e)}")

if __name__ == "__main__":
    main()