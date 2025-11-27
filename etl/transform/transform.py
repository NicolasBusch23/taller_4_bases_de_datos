import csv
import logging
from typing import Dict, Iterable, List

from etl.common.config import load_config
from etl.common.db import get_mongo_collection


log = logging.getLogger(__name__)


def _normalize(doc: Dict) -> Dict:
    """Project and standardize raw PokeAPI doc into a flat record."""
    types: List[str] = [t.get("type", {}).get("name", "") for t in doc.get("types", [])]
    abilities: List[str] = [a.get("ability", {}).get("name", "") for a in doc.get("abilities", [])]

    return {
        "id": doc.get("id"),
        "name": str(doc.get("name", "")).upper(),  # standardize to upper-case
        "height": doc.get("height"),
        "weight": doc.get("weight"),
        "base_experience": doc.get("base_experience"),
        "primary_type": types[0] if types else None,
        "types": ",".join(filter(None, types)),
        "abilities": ",".join(filter(None, abilities)),
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
    """TRANSFORM: Read RAW from MongoDB, standardize, and write CSV."""
    cfg = load_config()
    raw_col = get_mongo_collection(cfg, cfg["MONGO_RAW_COLLECTION"])

    cursor = raw_col.find({}, {"_id": 0})  # exclude MongoDB _id
    records = (_normalize(doc) for doc in cursor)

    out_path = "data/transformed/pokemon.csv"
    log.info("Starting TRANSFORM: writing standardized CSV to %s", out_path)
    count = _write_csv(records, out_path)
    log.info("TRANSFORM done. Wrote %d records.", count)
