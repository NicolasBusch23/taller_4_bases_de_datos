import csv
import logging
from typing import List, Tuple, Optional

from etl.common.config import load_config
from etl.common.db import get_mysql_connection


log = logging.getLogger(__name__)


def _ensure_schema(conn) -> None:
    """Create target table if not exists in MySQL."""
    create_sql = (
        """
        CREATE TABLE IF NOT EXISTS `juegos` (
            `id` INT PRIMARY KEY,
            `title` VARCHAR(150) NOT NULL,
            `genre` VARCHAR(50) NOT NULL,
            `platform` VARCHAR(50) NOT NULL,
            `developer` VARCHAR(100) NOT NULL,
            `release_date` DATE NULL,
            `short_description` TEXT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )
    with conn.cursor() as cur:
        cur.execute(create_sql)
    conn.commit()


def _parse_row(row: dict) -> Tuple[
    int, str, str, str, str, Optional[str], Optional[str]
]:
    """
    Convert CSV row into a tuple with correct Python types
    matching the MySQL schema.
    """

    def _to_date(v):
        if v in ("", None):
            return None
        return v  # MySQL acepta YYYY-MM-DD como DATE

    return (
        int(row["id"]),
        str(row["title"]),
        str(row["genre"]),
        str(row["platform"]),
        str(row["developer"]),
        _to_date(row.get("release_date")),
        row.get("short_description") or None,
    )


def _load_csv_into_mysql(csv_path: str, conn) -> int:
    """Load CSV rows into MySQL table juegos with upsert."""
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        tuples: List[Tuple] = [_parse_row(r) for r in reader]

    if not tuples:
        return 0

    insert_sql = (
        """
        INSERT INTO `juegos`
        (id, title, genre, platform, developer, release_date, short_description)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            title=VALUES(title),
            genre=VALUES(genre),
            platform=VALUES(platform),
            developer=VALUES(developer),
            release_date=VALUES(release_date),
            short_description=VALUES(short_description)
        """
    )
    with conn.cursor() as cur:
        cur.executemany(insert_sql, tuples)
    conn.commit()
    return len(tuples)


def load_main() -> None:
    """LOAD: Read transformed CSV and load into MySQL database."""
    cfg = load_config()
    csv_path = "data/transformed/juegos.csv"

    conn = get_mysql_connection(cfg)
    try:
        _ensure_schema(conn)
        log.info("Starting LOAD: loading CSV into MySQL")
        count = _load_csv_into_mysql(csv_path, conn)
        log.info("LOAD done. Upserted %d records into table JUEGOS.", count)
    finally:
        conn.close()
