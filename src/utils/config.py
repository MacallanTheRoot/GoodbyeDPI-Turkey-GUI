"""Per-user settings; the application directory can remain read-only."""
import json
from pathlib import Path

from .paths import config_dir


class ConfigManager:
    def __init__(self, directory: Path | None = None):
        self.config_file = (directory or config_dir()) / "config.json"
        self.default_config = {"dns_provider": "Turkey DNSRedir", "theme": "System"}
        self.config = self.load_config()

    def load_config(self):
        try:
            with self.config_file.open("r", encoding="utf-8") as stream:
                data = json.load(stream)
            return {**self.default_config, **data} if isinstance(data, dict) else self.default_config.copy()
        except (FileNotFoundError, ValueError, OSError):
            return self.default_config.copy()

    def save_config(self, key, value):
        self.config[key] = value
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.config_file.with_suffix(".tmp")
        with temporary.open("w", encoding="utf-8") as stream:
            json.dump(self.config, stream, indent=2)
        temporary.replace(self.config_file)

    def get(self, key):
        return self.config.get(key, self.default_config.get(key))
