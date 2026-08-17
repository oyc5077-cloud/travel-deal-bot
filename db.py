"""
가격 이력을 SQLite 파일 하나에 저장/조회하는 모듈.
DB 서버가 필요 없어서 완전 무료 - repo 안의 price_history.db 파일이 곧 DB.
"""
import sqlite3
from contextlib import contextmanager
from datetime import datetime

DB_PATH = "price_history.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS price_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_type TEXT NOT NULL,      -- 'flight' or 'hotel'
    item_name TEXT NOT NULL,      -- config.yaml의 name
    price REAL NOT NULL,
    currency TEXT DEFAULT 'KRW',
    checked_at TEXT NOT NULL,     -- ISO timestamp
    raw_meta TEXT                 -- 원본 응답 요약 (JSON 문자열)
);
CREATE INDEX IF NOT EXISTS idx_item_name ON price_log(item_name);
"""


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)


def insert_price(item_type: str, item_name: str, price: float,
                  currency: str = "KRW", raw_meta: str = ""):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO price_log (item_type, item_name, price, currency, checked_at, raw_meta) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (item_type, item_name, price, currency,
             datetime.utcnow().isoformat(), raw_meta),
        )


def get_history(item_name: str, limit_days: int = 90):
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT price, checked_at FROM price_log "
            "WHERE item_name = ? ORDER BY checked_at DESC LIMIT ?",
            (item_name, limit_days),
        )
        return cur.fetchall()


def get_all_latest():
    """각 item_name별 가장 최근 가격 1건씩 조회 (리포트용)."""
    with get_conn() as conn:
        cur = conn.execute(
            """
            SELECT item_type, item_name, price, currency, checked_at
            FROM price_log p1
            WHERE checked_at = (
                SELECT MAX(checked_at) FROM price_log p2
                WHERE p2.item_name = p1.item_name
            )
            ORDER BY item_type, item_name
            """
        )
        return cur.fetchall()
