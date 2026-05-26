from datetime import datetime

def generate_timestamp_name(folder_name: str) -> str:
    """
    Menghasilkan nama folder baru dengan format: NamaFolder_YYYYMMDD_HHMMSS
    Contoh: Project_20260526_143022
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{folder_name}_{timestamp}"

def log_status(status_type: str, message: str):
    """
    Helper untuk standarisasi print status di terminal agar terlihat rapi di konten.
    """
    prefix = {
        "INFO": "[*]",
        "SUCCESS": "[V]",
        "ERROR": "[-]",
        "ALERT": "[!]"
    }
    
    selected_prefix = prefix.get(status_type.upper(), "[?]")
    print(f"{selected_prefix} {message}")