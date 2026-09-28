import os
from pathlib import Path

# Base backend directory
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

def load_environment():
    """Loads environment variables from backend/.env if present"""
    if ENV_FILE.exists():
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip()
                    if key and key not in os.environ:
                        os.environ[key] = val

load_environment()

NASA_API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")
EARTHDATA_USERNAME = os.getenv("EARTHDATA_USERNAME", "")
EARTHDATA_BEARER_TOKEN = os.getenv("EARTHDATA_BEARER_TOKEN", "")
FIRMS_MAP_KEY = os.getenv("FIRMS_MAP_KEY", "")
