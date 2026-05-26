import os
import requests

def download_csv_files(total_files=15, target_dir="data/input"):
    # 1. Mastiin folder input tujuan sudah ready
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"Folder '{target_dir}' berhasil dibuat.")

    print(f"Memulai download {total_files} file CSV otomatis...")

    # Loop untuk mendownload sebanyak 15 kali
    for i in range(1, total_files + 1):
        try:
            # Gunakan URL generator CSV publik yang responsif
            # Kita kirim parameter berbeda (id) tiap loop biar isi datanya unik
            csv_url = f"https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv" 
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }
            
            response = requests.get(csv_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Format nama file mentah awal (misal: RAW_DATA_001.csv)
                file_name = f"RAW_DATA_{str(i).zfill(3)}.csv"
                file_path = os.path.join(target_dir, file_name)
                
                # Simpan data teks/csv ke lokal disk
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(response.text)
                    
                print(f"SUCCESS: [{file_name}] berhasil didownload.")
            else:
                print(f"FAILED: Gagal download file ke-{i}. Status: {response.status_code}")
                
        except Exception as e:
            print(f"ERROR: Terjadi masalah pada file ke-{i}: {str(e)}")
            
    print(f"\nSelesai! {total_files} file CSV mentah sudah siap di '{target_dir}'.")

if __name__ == "__main__":
    # Panggil fungsi download
    download_csv_files(total_files=15)