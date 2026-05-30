import os
import csv
from src.orchestrator import CleanerOrchestrator

def main():
    # 1. Inisialisasi Jalur File (Path)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    input_file_path = os.path.join(BASE_DIR, "data", "raw_marketplace.csv")
    output_file_path = os.path.join(BASE_DIR, "data", "cleaned_marketplace.csv")

    # Pastikan file input ada
    if not os.path.exists(input_file_path):
        print(f"Error: File {input_file_path} tidak ditemukan!")
        print("Silakan buat foldernya dan taruh data mentah di sana terlebih dahulu.")
        return

    # 2. Inisialisasi Engine
    engine = CleanerOrchestrator()
    
    print("=== STARTING DATA CLEANING PROCESS ===")
    print(f"Membaca data dari: {input_file_path}")

    # 3. Proses Membaca, Membersihkan, dan Menulis Data
    try:
        with open(input_file_path, mode='r', encoding='utf-8') as infile, \
             open(output_file_path, mode='w', encoding='utf-8', newline='') as outfile:
            
            reader = csv.DictReader(infile)
            # Ambil nama kolom asli dari file mentah
            fieldnames = reader.fieldnames
            
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()  # Tulis baris judul kolom (No, Nama_Produk_Mentah, dll)

            count = 0
            for row in reader:
                # Ambil teks kotor pada kolom Nama_Produk_Mentah
                raw_text = row['Nama_Produk_Mentah']
                
                # Bersihkan menggunakan Engine Python kita
                cleaned_text = engine.process_text(raw_text)
                
                # Masukkan kembali teks yang sudah bersih ke kolom yang sama
                row['Nama_Produk_Mentah'] = cleaned_text
                
                # Tulis baris baru ke file output
                writer.writerow(row)
                count += 1
                
        print(f"Sukses! {count} baris data berhasil dibersihkan.")
        print(f"Hasil pembersihan disimpan di: {output_file_path}")
        print("=== PROCESS COMPLETED ===")

    except Exception as e:
        print(f"Terjadi kesalahan saat memproses data: {e}")

if __name__ == "__main__":
    main()