import os
import requests

def download_sepatu_images(total_images=15, target_dir="data/input"):
    # 1. Mastiin folder input udah ada
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"Folder '{target_dir}' berhasil dibuat.")

    print(f"Memulai download {total_images} foto sepatu otomatis...")

    # Kita pakai Unsplash Source buat dapetin gambar sepatu random yang HD
    # format: https://images.unsplash.com/photo-...
    url = "https://public-api.wordpress.com/wpcom/v2/sites/61051560/media" 
    # Alternatif paling gampang & gak ribet pake langsung link randomizer Unsplash:
    base_url = "https://source.unsplash.com/featured/?shoes"
    
    # Karena Unsplash Source kadang sering redirect, kita pakai cara yang lebih reliable:
    # Kita hit API LoremFlickr atau Unsplash Source langsung via requests
    
    success_count = 0
    for i in range(1, total_images + 1):
        try:
            # Gunakan header biar gak disangka bot jahat
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            
            # Kita tambah parameter random `sig` biar gambarnya gak kembar semua
            image_url = f"https://loremflickr.com/800/800/shoes,sneakers?lock={i}"
            
            # Request ke server gambar
            response = requests.get(image_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Format nama file mentah (misal: IMG_RAW_001.jpg)
                # Sesuai prinsip kemarin, kita simpan dengan padding zero
                file_name = f"IMG_RAW_{str(i).zfill(3)}.jpg"
                file_path = os.path.join(target_dir, file_name)
                
                # Write file fisis ke dalam disk (Single Writer Principle)
                with open(file_path, "wb") as f:
                    f.write(response.content)
                    
                print(f"SUCCESS: [{file_name}] berhasil didownload.")
                success_count += 1
            else:
                print(f"FAILED: Gagal download gambar ke-{i}. Status code: {response.status_code}")
                
        except Exception as e:
            print(f"ERROR: Ada masalah saat download gambar ke-{i}: {str(e)}")
            
    print(f"\nSelesai! {success_count}/{total_images} foto sepatu siap di '{target_dir}'.")

if __name__ == "__main__":
    download_sepatu_images(total_images=15)