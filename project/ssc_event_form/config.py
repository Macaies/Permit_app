import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
# SQLite (dev) by default; override with DATABASE_URL for cloud (e.g. Postgres)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'events.db'}")
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", str(BASE_DIR / "uploads"))
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
