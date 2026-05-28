import json
import os
from core.cleaner import DuplicateCleanerEngine

def load_config():
    config_path = os.path.join("config", "pipeline_config.json")
    with open(config_path, "r") as file:
        return json.load(file)

if __name__ == "__main__":
    try:
        config = load_config()
        engine = DuplicateCleanerEngine(config)
        engine.run()
    except Exception as e:
        print(f"[FATAL ERROR] Engine berhenti mendadak: {e}")