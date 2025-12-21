import logging
from typing import Dict, List

import requests

from etl.common.config import load_config  # Cargar configuraciones guardadas en etl/common
from etl.common.db import get_mongo_collection


log = logging.getLogger(__name__)

#-- Para traer los datos de la API 
def _fetch_games_list(base_url: str) -> List[Dict]:
    """Fetch list of games from FreeToGame API (RAW JSON)."""
    resp = requests.get(base_url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data  # La API ya retorna una lista de juegos


#-- Para extraer los datos y abrir una conexión con MongoDB
def extract_main() -> None:
    """EXTRACT: Fetch JSON from FreeToGame API and upsert RAW docs into MongoDB."""
    cfg = load_config()
    raw_col = get_mongo_collection(cfg, cfg["MONGO_RAW_COLLECTION"])

    base_url: str = cfg["JUEGOS_BASE_URL"]
    limit: int = cfg["JUEGOS_LIMIT"]

    #Extracción de Datos Crudos
    log.info("Starting EXTRACT: fetching games from FreeToGame API")
    games = _fetch_games_list(base_url)

    # Aplicar límite definido en configuración
    games = games[:limit]
    log.info("Fetched %d games. Storing RAW documents...", len(games))

    upserted = 0
    for game in games:
        try:
            # Se usa el 'id' del juego como clave natural para upsert
            raw_col.replace_one(
                {"id": game.get("id")},
                game,
                upsert=True
            )
            upserted += 1
        except Exception as exc:  # keep demo simple
            log.warning("Failed to upsert game %s: %s", game.get("title"), exc)

    log.info("EXTRACT done. Upserted %d raw documents into MongoDB.",upserted)  # Guarda los datos en MongoDB