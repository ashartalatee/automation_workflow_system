import pandas as pd
from typing import List

class DuplicateStrategy:
    @staticmethod
    def resolve_columns(strategy_type: str, custom_cols: List[str] = None) -> List[str]:
        """Memetakan tipe strategi ke kolom target"""
        strategy_map = {
            "sku": ["sku"],
            "email": ["email"],
            "combination": custom_cols if custom_cols else []
        }
        
        target = strategy_map.get(strategy_type.lower())
        if not target:
            raise ValueError(f"Strategi '{strategy_type}' tidak valid atau kolom kombinasi kosong.")
        return target

    @staticmethod
    def clean(df: pd.DataFrame, subset_columns: List[str]) -> pd.DataFrame:
        """Melakukan audit jumlah duplikat dan mengeksekusi drop_duplicates"""
        # Validasi apakah kolom ada di dataframe
        missing_cols = [col for col in subset_columns if col not in df.columns]
        if missing_cols:
            raise KeyError(f"Kolom target tidak ditemukan di data: {missing_cols}")
        
        # 1. Skill: duplicated() untuk hitung total duplikat (sebelum di-drop)
        total_duplicates = df.duplicated(subset=subset_columns, keep='first').sum()
        print(f"[AUDIT] Menemukan {total_duplicates} baris duplikat berdasarkan kolom: {subset_columns}")
        
        # 2. Skill: drop_duplicates() untuk membersihkan data
        df_cleaned = df.drop_duplicates(subset=subset_columns, keep='first')
        return df_cleaned