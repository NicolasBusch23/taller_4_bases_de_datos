import os
from pathlib import Path
from typing import Dict, Any

from dotenv import load_dotenv


def load_config() -> Dict[str, Any]:
    """Load configuration from .env with safe defaults and ensure data dirs."""
    load_dotenv()

    cfg: Dict[str, Any] = {
        "MONGO_URI": os.getenv("MONGO_URI", "mongodb://localhost:27017"), #Dirección para conectarse a MongoDB
        #Se le pide que se conecte a MongoDB usando la URI definida en el sistema; si no hay ninguna, usar MongoDB local
        "MONGO_DB": os.getenv("MONGO_DB", "taller4_db"), #Base de datos a utilizar 
        #El nombre de la base de datos de MongoDB será el que esté definido en el sistema; si no hay ninguno definido, usar 'taller4_db'.
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
