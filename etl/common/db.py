from typing import Any, Tuple
from urllib.parse import urlparse, unquote

from pymongo import MongoClient
import pymysql


def get_mongo_collection(cfg: dict, collection_name: str):
    """Return a MongoDB collection using cfg values."""
    client = MongoClient(cfg["MONGO_URI"])
    db = client[cfg["MONGO_DB"]]
    return db[collection_name]

def _parse_mysql_url(url: str) -> Tuple[str, str, str, int, str]:
    """Parse mysql+pymysql URL to (user, password, host, port, db)."""
    parsed = urlparse(url)
    user = unquote(parsed.username or "")
    password = unquote(parsed.password or "")
    host = parsed.hostname or "localhost"
    port = int(parsed.port or 3306)
    db = (parsed.path or "/").lstrip("/") or "pokemon"
    return user, password, host, port, db


def ensure_mysql_database(url: str) -> None:
    """Ensure target MySQL database exists, creating it if necessary."""
    user, password, host, port, db = _parse_mysql_url(url)
    # Connect without database to create it if missing
    conn = pymysql.connect(host=host, user=user, password=password, port=port, charset="utf8mb4")
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{db}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        conn.commit()
    finally:
        conn.close()


def get_mysql_connection(cfg: dict) -> pymysql.connections.Connection:
    """Return a MySQL connection, creating the DB if it does not exist."""
    url: str = cfg["DATABASE_URL"]
    user, password, host, port, db = _parse_mysql_url(url)
    ensure_mysql_database(url)
    conn = pymysql.connect(
        host=host,
        user=user,
        password=password,
        port=port,
        database=db,
        charset="utf8mb4",
        autocommit=False,
    )
    return conn
