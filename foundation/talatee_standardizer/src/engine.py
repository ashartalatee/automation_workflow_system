import pandas as pd
from src.core.normalizer import ColumnNormalizer

class ColumnStandardizerEngine:
    def __init__(self):
        self.normalizer = ColumnNormalizer()

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Menerima DataFrame, melakukan standarisasi nama kolom,
        dan otomatis menangani nama kolom yang duplikat setelah normalisasi.
        """
        if df.empty:
            return df
            
        cloned_df = df.copy()
        
        new_columns = []
        seen_columns = {}
        
        for col in cloned_df.columns:
            # 1. Bersihkan nama kolom menggunakan normalizer berbasis Regex
            clean_name = self.normalizer.clean(col)
            
            # 2. Deduplication Logic: Jika nama kolom sudah pernah ada, tambahkan suffix angka
            if clean_name in seen_columns:
                seen_columns[clean_name] += 1
                final_name = f"{clean_name}_{seen_columns[clean_name]}"
            else:
                seen_columns[clean_name] = 0
                final_name = clean_name
                
            new_columns.append(final_name)
        
        # 3. Terapkan nama kolom baru yang sudah bersih dan unik
        cloned_df.columns = new_columns
        return cloned_df