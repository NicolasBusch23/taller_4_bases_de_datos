import os
from pathlib import Path
from typing import Dict, Any

from dotenv import load_dotenv


def load_config() -> Dict[str, Any]:
    """Load configuration from .env with safe defaults and ensure data dirs."""
    load_dotenv()

    cfg: Dict[str, Any] = {
        "MONGO_URI": os.getenv("MONGO_URI", "mongodb://localhost:27017"),
        "MONGO_DB": os.getenv("MONGO_DB", "etl_demo"),
        "MONGO_RAW_COLLECTION": os.getenv("MONGO_RAW_COLLECTION", "pokemon_raw"),
        "POKEAPI_BASE_URL": os.getenv("POKEAPI_BASE_URL", "https://pokeapi.co/api/v2"),
        "POKEAPI_LIMIT": int(os.getenv("POKEAPI_LIMIT", "25")),
        # MySQL connection URL, e.g. mysql+pymysql://user:pass@host:3306/pokemon
        "DATABASE_URL": os.getenv("DATABASE_URL", "mysql+pymysql://root:root@localhost:3306/pokemon"),
    }

    # Ensure data directories exist
    Path("data").mkdir(parents=True, exist_ok=True)
    Path("data/transformed").mkdir(parents=True, exist_ok=True)
    return cfg
