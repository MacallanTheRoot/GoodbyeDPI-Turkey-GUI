"""Small UI-facing snapshot; service state is never inferred from widgets."""
from dataclasses import dataclass, field
from enum import Enum


DNS_PROVIDERS = {
    "Turkey DNSRedir": ("77.88.8.8", "1253"),
    "Yandex (Standard)": ("77.88.8.8", "1253"),
    "Google": ("8.8.8.8", "53"),
    "Cloudflare": ("1.1.1.1", "53"),
    "OpenDNS": ("208.67.222.222", "53"),
}


class Phase(Enum):
    INACTIVE = "inactive"
    STARTING = "starting"
    ACTIVE = "active"
    STOPPING = "stopping"
    ERROR = "error"
    SHUTTING_DOWN = "shutting_down"


@dataclass
class AppState:
    platform: str
    phase: Phase = Phase.INACTIVE
    dns_provider: str = "Turkey DNSRedir"
    startup_enabled: bool = False
    theme: str = "System"
    activity_expanded: bool = False
    messages: list[str] = field(default_factory=list)
    error: str = ""

    @property
    def active(self):
        return self.phase == Phase.ACTIVE

    @property
    def heading(self):
        prefix = "Protection" if self.platform == "windows" else "Local Proxy"
        return f"{prefix} {'Active' if self.active else 'Inactive'}"

    @property
    def detail(self):
        if self.phase == Phase.STARTING:
            return "Starting GoodbyeDPI…" if self.platform == "windows" else "Starting local proxy…"
        if self.phase == Phase.STOPPING:
            return "Stopping GoodbyeDPI…" if self.platform == "windows" else "Stopping local proxy…"
        if self.phase == Phase.ERROR:
            return self.error
        if self.platform == "windows":
            return ("GoodbyeDPI is running. DNS selection is locked while active." if self.active else
                    "GoodbyeDPI is ready. Select Enable to start protection.")
        return ("Applications must use 127.0.0.1:8080 to use this proxy." if self.active else
                "SpoofDPI is ready. Applications need to use the local proxy.")

    @property
    def backend_label(self):
        return "GoodbyeDPI · DNS redirection" if self.platform == "windows" else "SpoofDPI · local HTTP proxy"
