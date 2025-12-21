import csv
import logging
from typing import Dict, Iterable

from etl.common.config import load_config
from etl.common.db import get_mongo_collection

log = logging.getLogger(__name__)


def _normalize(doc: Dict) -> Dict:
    """Project and standardize raw FreeToGame doc into a flat record."""

    return {
        "id": doc.get("id"),  # ID original de la API (clave natural)
        "title": str(doc.get("title", "")).strip(),
        "genre": str(doc.get("genre", "")).strip(),
        "platform": str(doc.get("platform", "")).strip(),
        "developer": str(doc.get("developer", "")).strip(),
        "release_date": doc.get("release_date"), # Se conserva el formato YYYY-MM-DD para facilitar su conversión posterior a tipo fecha
        "short_description": str(doc.get("short_description", "")).strip(),
    }


def _write_csv(rows: Iterable[Dict], path: str) -> int:
    """Write iterable of rows to CSV and return row count."""
    rows = list(rows)
    if not rows:
        return 0

    header = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)

    return len(rows)


def transform_main() -> None:
    """TRANSFORM: Read RAW from MongoDB, select fields, and write CSV."""
    cfg = load_config()
    raw_col = get_mongo_collection(cfg, cfg["MONGO_RAW_COLLECTION"])

    # Se excluye el _id interno de MongoDB
    cursor = raw_col.find({}, {"_id": 0})

    # Normalización de documentos RAW
    records = (_normalize(doc) for doc in cursor)

    out_path = "data/transformed/juegos.csv"  # Se guardarán los datos en un .csv
    log.info("Starting TRANSFORM: writing standardized CSV to %s", out_path)
    count = _write_csv(records, out_path)
    log.info("TRANSFORM done. Wrote %d records.", count)