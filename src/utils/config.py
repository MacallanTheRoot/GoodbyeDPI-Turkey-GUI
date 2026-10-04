"""Per-user settings; the application directory can remain read-only."""
import json
import os
import tempfile
from pathlib import Path

from .paths import config_dir, resource_path


class ConfigManager:
    def __init__(self, directory: Path | None = None):
        self.config_file = (Path(directory) if directory is not None else config_dir()) / "config.json"
        self.default_config = {"dns_provider": "Turkey DNSRedir", "theme": "System"}
        if directory is None:
            self._migrate_legacy()
        self.config = self.load_config()

    def _migrate_legacy(self):
        legacy = resource_path("config.json")
        try:
            if self.config_file.exists() or not legacy.is_file() or legacy == self.config_file:
                return
            data = json.loads(legacy.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                self.config_file.parent.mkdir(parents=True, exist_ok=True)
                # Exclusive creation never replaces settings created concurrently.
                with self.config_file.open("x", encoding="utf-8") as destination:
                    json.dump(data, destination, indent=2)
        except (OSError, ValueError, FileExistsError):
            pass  # Invalid or inaccessible legacy settings leave defaults available.

    def load_config(self):
        try:
            with self.config_file.open("r", encoding="utf-8") as stream:
                data = json.load(stream)
            return {**self.default_config, **data} if isinstance(data, dict) else self.default_config.copy()
        except (FileNotFoundError, ValueError, OSError):
            return self.default_config.copy()

    def save_config(self, key, value):
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        updated = {**self.config, key: value}
        descriptor, name = tempfile.mkstemp(prefix=".config-", suffix=".tmp", dir=self.config_file.parent)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                json.dump(updated, stream, indent=2)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name, self.config_file)
        finally:
            Path(name).unlink(missing_ok=True)
        self.config = updated

    def get(self, key):
        return self.config.get(key, self.default_config.get(key))
