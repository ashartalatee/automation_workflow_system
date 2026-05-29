import re

class ColumnNormalizer:
    @staticmethod
    def clean(column_name: str) -> str:
        if not isinstance(column_name, str):
            return ""
        
        # 1. Trim whitespace di awal dan akhir
        text = column_name.strip()
        
        # 2. Tangani singkatan/Capslock berturut-turut sebelum memisahkan CamelCase
        # Contoh: CustomerID -> Customer_ID atau SKUInduk -> SKU_Induk
        text = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', text)
        
        # 3. Ubah CamelCase standar menjadi snake_case (Contoh: NamaProduk -> Nama_Produk)
        text = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', text)
        
        # 4. Ganti spasi, strip, tanda kurung, atau karakter non-alphanumeric dengan underscore
        text = re.sub(r'[\s\-\[\]\(\)\!\?]+', '_', text)
        
        # 5. Hapus karakter spesial murni yang tersisa
        text = re.sub(r'[^a-zA-Z0-9_]', '', text)
        
        # 6. Sikat multiple underscore berturut-turut (Contoh: nama__produk -> nama_produk)
        text = re.sub(r'_+', '_', text)
        
        # 7. Bersihkan underscore jika ada di paling awal atau akhir setelah proses regex
        text = text.strip('_')
        
        # 8. Convert ke lowercase penuh
        return text.lower()