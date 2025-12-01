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
        CREATE TABLE IF NOT EXISTS `POKEMON` (
            `id` INT PRIMARY KEY,
            `name` VARCHAR(100) NOT NULL,
            `height` DECIMAL(5,2) NULL,
            `weight` DECIMAL(7,2) NULL,
            `base_experience` INT NULL,
            `primary_type` VARCHAR(50) NULL,
            `types` TEXT NULL,
            `abilities` TEXT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )
    with conn.cursor() as cur:
        cur.execute(create_sql)
        # If the table already existed with INT columns, migrate to DECIMAL
        cur.execute(
            """
            SELECT COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'POKEMON' AND COLUMN_NAME IN ('height','weight')
            """
        )
        col_types = {row[0].lower(): row[1].lower() for row in cur.fetchall()}
        if col_types.get('height') not in (None, 'decimal'):
            cur.execute("ALTER TABLE `POKEMON` MODIFY COLUMN `height` DECIMAL(5,2) NULL")
        if col_types.get('weight') not in (None, 'decimal'):
            cur.execute("ALTER TABLE `POKEMON` MODIFY COLUMN `weight` DECIMAL(7,2) NULL")
    conn.commit()


def _parse_row(row: dict) -> Tuple[int, str, Optional[float], Optional[float], Optional[int], Optional[str], Optional[str], Optional[str]]:
    def _to_int(v):
        if v == "" or v is None:
            return None
        try:
            return int(float(v))
        except (ValueError, TypeError):
            return None

    def _to_float(v):
        if v == "" or v is None:
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            return None

    return (
        int(row["id"]),
        str(row["name"]),
        _to_float(row.get("height")),
        _to_float(row.get("weight")),
        _to_int(row.get("base_experience")),
        row.get("primary_type") or None,
        row.get("types") or None,
        row.get("abilities") or None,
    )


def _load_csv_into_mysql(csv_path: str, conn) -> int:
    """Load CSV rows into MySQL table POKEMON with upsert."""
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        tuples: List[Tuple] = [_parse_row(r) for r in reader]

    if not tuples:
        return 0

    insert_sql = (
        """
        INSERT INTO `POKEMON` (id, name, height, weight, base_experience, primary_type, types, abilities)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            name=VALUES(name),
            height=VALUES(height),
            weight=VALUES(weight),
            base_experience=VALUES(base_experience),
            primary_type=VALUES(primary_type),
            types=VALUES(types),
            abilities=VALUES(abilities)
        """
    )
    with conn.cursor() as cur:
        cur.executemany(insert_sql, tuples)
    conn.commit()
    return len(tuples)


def load_main() -> None:
    """LOAD: Read transformed CSV and load into MySQL database."""
    cfg = load_config()
    csv_path = "data/transformed/pokemon.csv"

    conn = get_mysql_connection(cfg)
    try:
        _ensure_schema(conn)
        log.info("Starting LOAD: loading CSV into MySQL")
        count = _load_csv_into_mysql(csv_path, conn)
        log.info("LOAD done. Upserted %d records into table POKEMON.", count)
    finally:
        conn.close()
