import json
import os

def load_config(config_path="config/mapping.json"):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Konfigurasi tidak ditemukan di {config_path}")
    with open(config_path, "r") as f:
        return json.load(f)