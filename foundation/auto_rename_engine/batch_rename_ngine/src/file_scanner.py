import os

def scan_input_files(input_dir, extension):
    """Mengambil semua file di folder input yang memiliki ekstensi yang sesuai, terurut."""
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        return []
    
    files = [f for f in os.listdir(input_dir) if f.lower().endswith(extension.lower())]
    # Urutkan secara alfabetis agar index penomoran konsisten
    return sorted(files)