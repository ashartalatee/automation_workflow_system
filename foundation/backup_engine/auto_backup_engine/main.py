from src.config_loader import load_engine_config
from src.backup_service import BackupEngine
from src.utils import log_status

def main():
    print("="*40)
    print("      TALATEE AUTO-BACKUP ENGINE      ")
    print("="*40)
    
    try:
        # Memuat konfigurasi menggunakan loader baru
        config = load_engine_config()
        
        # Inisialisasi dan jalankan engine
        engine = BackupEngine(
            source_path=config["source_dir"],
            backup_base_path=config["backup_dir"]
        )
        engine.execute()
        
    except Exception as e:
        log_status("ERROR", f"Critical Failure: {e}")
    
    print("="*40)

if __name__ == "__main__":
    main()