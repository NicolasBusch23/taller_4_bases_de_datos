import logging
from typing import Dict, List

import requests

from etl.common.config import load_config
from etl.common.db import get_mongo_collection


log = logging.getLogger(__name__)


def _fetch_pokemon_list(base_url: str, limit: int) -> List[Dict]:
    """Fetch list of Pokemon entries from PokeAPI (name + detail URL)."""
    url = f"{base_url}/pokemon?limit={limit}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("results", [])


def _fetch_pokemon_detail(detail_url: str) -> Dict:
    """Fetch a single Pokemon detail JSON from PokeAPI."""
    resp = requests.get(detail_url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def extract_main() -> None:
    """EXTRACT: Fetch JSON from PokeAPI and upsert RAW docs into MongoDB."""
    cfg = load_config()
    raw_col = get_mongo_collection(cfg, cfg["MONGO_RAW_COLLECTION"])

    limit: int = cfg["POKEAPI_LIMIT"]
    base_url: str = cfg["POKEAPI_BASE_URL"]

    log.info("Starting EXTRACT: fetching list from PokeAPI (limit=%s)", limit)
    entries = _fetch_pokemon_list(base_url, limit)
    log.info("Fetched %d entries. Downloading details...", len(entries))

    upserted = 0
    for e in entries:
        try:
            detail = _fetch_pokemon_detail(e["url"])
            # Use PokeAPI 'id' as natural key for upsert
            raw_col.replace_one({"id": detail.get("id")}, detail, upsert=True)
            upserted += 1
        except Exception as exc:  # keep demo simple
            log.warning("Failed to fetch/upsert %s: %s", e, exc)

    log.info("EXTRACT done. Upserted %d raw documents into MongoDB.", upserted)
