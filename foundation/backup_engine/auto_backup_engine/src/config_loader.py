import json
from pathlib import Path

def load_engine_config(config_file_name: str = "settings.json") -> dict:
    """
    Mencari dan membaca file konfigurasi di dalam folder 'config'.
    Menggunakan pathlib agar aman dijalankan di Windows maupun Linux/Mac.
    """
    # Menentukan base directory projek (1 tingkat di atas folder src)
    project_root = Path(__file__).resolve().parent.parent
    config_path = project_root / "config" / config_file_name

    # Validasi apakah file config ada
    if not config_path.exists():
        raise FileNotFoundError(
            f"[-] Critical Error: File konfigurasi tidak ditemukan di: {config_path}\n"
            f"Silakan buat file tersebut terlebih dahulu."
        )

    # Membaca file JSON
    with open(config_path, "r") as file:
        try:
            config_data = json.load(file)
            return config_data
        except json.JSONDecodeError:
            raise ValueError(f"[-] Error: Format JSON di {config_file_name} tidak valid!")