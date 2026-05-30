import re
import unicodedata

class InvalidCharacterCleaner:
    def __init__(self):
        # 1. Pattern khusus untuk mendeteksi karakter TM
        self.tm_pattern = re.compile(r'™', re.UNICODE)
        
        # 2. Strict Pattern: Hanya sisakan Huruf (A-Z, a-z), Angka (0-9), dan Spasi (\s)
        # Semua simbol, tanda baca, kurung, dan emoji akan langsung terhapus
        self.strict_clean_pattern = re.compile(r'[^A-Za-z0-9\s]', re.UNICODE)
        
        # 3. Pattern untuk merapikan spasi ganda
        self.multiple_spaces_pattern = re.compile(r'\s+')

    def clean(self, text: str) -> str:
        if not text:
            return ""

        # Langkah 1: Normalisasi Unicode standar
        normalized_text = unicodedata.normalize('NFKD', text)
        
        # Langkah 2: Ubah karakter ™ menjadi teks "TM" secara eksplisit
        text_with_tm = self.tm_pattern.sub('TM', normalized_text)
        
        # Langkah 3: Hapus total semua karakter yang BUKAN alfanumerik dan BUKAN spasi
        cleaned_text = self.strict_clean_pattern.sub('', text_with_tm)
        
        # Langkah 4: Bersihkan spasi ganda yang muncul akibat karakter yang dihapus
        cleaned_text = self.multiple_spaces_pattern.sub(' ', cleaned_text)
        
        # Langkah 5: Potong spasi di ujung awal dan akhir teks
        return cleaned_text.strip()