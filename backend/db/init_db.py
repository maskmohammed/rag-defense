import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]  # rag-defense/
DB_PATH = BASE_DIR / "data" / "db" / "rag.db"
SQL_PATH = Path(__file__).resolve().parent / "init_db.sql"

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    sql = SQL_PATH.read_text(encoding="utf-8")
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(sql)
        conn.commit()
    finally:
        conn.close()

    print(f"OK - Base initialisée : {DB_PATH}")

if __name__ == "__main__":
    init_db()
