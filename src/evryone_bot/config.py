import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True, slots=True)
class Settings:
    telegram_api_key: str
    database_path: Path = Path("evryone.db")
    health_port: int | None = None

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        api_key = os.getenv("TELEGRAM_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("TELEGRAM_API_KEY is not set")
        health_port_value = os.getenv("HEALTH_PORT", "").strip()
        health_port = int(health_port_value) if health_port_value else None
        if health_port is not None and not 1 <= health_port <= 65535:
            raise ValueError("HEALTH_PORT must be between 1 and 65535")
        return cls(telegram_api_key=api_key, health_port=health_port)
