import json
import os

class ConfigManager:
    def __init__(self, config_dir):
        self.config_file = os.path.join(config_dir, "config.json")
        self.default_config = {
            "dns_provider": "Turkey DNSRedir",
        }
        self.config = self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_file):
            return self.default_config.copy()
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Merge with default to ensure all keys exist
                config = self.default_config.copy()
                config.update(data)
                return config
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.default_config.copy()

    def save_config(self, key, value):
        self.config[key] = value
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key):
        return self.config.get(key, self.default_config.get(key))
