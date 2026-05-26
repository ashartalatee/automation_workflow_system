import shutil
from pathlib import Path
from src.utils import generate_timestamp_name, log_status

class BackupEngine:
    def __init__(self, source_path: str, backup_base_path: str):
        self.source = Path(source_path)
        self.backup_base = Path(backup_base_path)

    def execute(self):
        # 1. Validasi folder sumber
        if not self.source.exists():
            log_status("ERROR", f"Folder sumber '{self.source}' tidak ditemukan!")
            return False

        # 2. Membuat nama folder tujuan menggunakan helper dari utils.py
        target_folder_name = generate_timestamp_name(self.source.name)
        destination = self.backup_base / target_folder_name

        try:
            log_status("INFO", f"Memulai backup dari: {self.source}")
            log_status("INFO", f"Menyalin ke: {destination}")
            
            # 3. Proses eksekusi copy folder
            shutil.copytree(self.source, destination)
            
            log_status("SUCCESS", "Backup Berhasil Dialokasikan dengan Aman!")
            return True
            
        except Exception as e:
            log_status("ERROR", f"Terjadi kesalahan saat proses backup: {str(e)}")
            return False