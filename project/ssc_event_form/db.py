import os
import sqlite3
from contextlib import contextmanager
from config import DATABASE_URL

# parse our SQLite path from DATABASE_URL like 'sqlite:///path/to/events.db'
def _sqlite_path(url: str) -> str:
    if not url.startswith("sqlite:///"):
        raise ValueError("Only SQLite URLs are supported in dev. Use DATABASE_URL=sqlite:///full/path.db")
    return url.replace("sqlite:///", "", 1)

DB_PATH = _sqlite_path(DATABASE_URL)

def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.row_factory = dict_factory
        conn.execute("PRAGMA foreign_keys = ON;")
        yield conn
    finally:
        conn.close()
