from src.core.cleaner import InvalidCharacterCleaner

class CleanerOrchestrator:
    def __init__(self):
        self.cleaner = InvalidCharacterCleaner()

    def process_text(self, raw_text: str) -> str:
        # Tempat menaruh logic pre-validation jika dibutuhkan
        if not isinstance(raw_text, str):
            raise ValueError("Input harus berupa string!")
            
        cleaned_result = self.cleaner.clean(raw_text)
        
        # Post-validation / Logging bisa ditaruh di sini
        return cleaned_result