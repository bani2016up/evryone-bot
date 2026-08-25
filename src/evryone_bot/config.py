import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True, slots=True)
class Settings:
    telegram_api_key: str
    database_path: Path = Path("evryone.db")

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        api_key = os.getenv("TELEGRAM_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("TELEGRAM_API_KEY is not set")
        return cls(telegram_api_key=api_key)
