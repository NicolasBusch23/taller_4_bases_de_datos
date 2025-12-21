import os
from pathlib import Path
from typing import Dict, Any

from dotenv import load_dotenv


def load_config() -> Dict[str, Any]:
    """Load configuration from .env with safe defaults and ensure data dirs."""
    load_dotenv()

    cfg: Dict[str, Any] = {
        "MONGO_URI": os.getenv("MONGO_URI", "mongodb://localhost:27017"),
        "MONGO_DB": os.getenv("MONGO_DB", "taller4_db"), #Base de datos a utilizar 
        "MONGO_RAW_COLLECTION": os.getenv("MONGO_RAW_COLLECTION", "raw_data"), #Datos crudos
        "JUEGOS_BASE_URL": os.getenv("JUEGOS_BASE_URL", "https://www.freetogame.com/api/games"),
        "JUEGOS_LIMIT": int(os.getenv("JUEGOS_LIMIT", "190")), #Límite de >=100 datos según el taller
        # MySQL connection URL, e.g. mysql+pymysql://user:pass@host:3306/juegos
        "DATABASE_URL": os.getenv("DATABASE_URL"),
    }

    # Ensure data directories exist
    Path("data").mkdir(parents=True, exist_ok=True)
    Path("data/transformed").mkdir(parents=True, exist_ok=True)
    return cfg
