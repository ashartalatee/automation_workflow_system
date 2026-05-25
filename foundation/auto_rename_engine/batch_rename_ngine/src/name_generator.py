import os

def generate_rename_map(input_files, config):
    """
    Memetakan nama lama ke nama baru dan memastikan tidak ada tabrakan nama.
    Menerapkan prinsip deterministik: Validasi total sebelum eksekusi.
    """
    rename_tasks = []
    seen_new_names = set()
    
    prefix = config["new_prefix"]
    padding = config["padding_zeros"]
    ext = config["target_extension"]
    
    for index, old_name in enumerate(input_files, start=1):
        # Format angka dengan padding zero (misal: 1 -> 001)
        counter_str = str(index).zfill(padding)
        new_name = f"{prefix}{counter_str}{ext}"
        
        # Deteksi duplikasi/bentrokan nama baru
        if new_name in seen_new_names:
            raise ValueError(f"FATAL: Deteksi bentrokan nama pada {new_name}. Evaluasi kembali konfigurasi Anda.")
            
        seen_new_names.add(new_name)
        rename_tasks.append({
            "old_name": old_name,
            "new_name": new_name
        })
        
    return rename_tasks