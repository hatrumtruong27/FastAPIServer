"""Runtime configuration for the FastAPI gateway."""

from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

load_dotenv(PROJECT_ROOT / ".env")


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/create_story")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-change-me-create-story")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRES = timedelta(minutes=_int_env("JWT_ACCESS_TOKEN_MINUTES", 30))
REFRESH_TOKEN_EXPIRES = timedelta(days=_int_env("JWT_REFRESH_TOKEN_DAYS", 14))
BOOTSTRAP_ADMIN_EMAIL = os.getenv("BOOTSTRAP_ADMIN_EMAIL", "admin@gmail.com")
BOOTSTRAP_ADMIN_PASSWORD = os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "+E8ep0m7(h5ut#Q$")
