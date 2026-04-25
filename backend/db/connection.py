import sqlite3
from pathlib import Path


# rag-defense/
BASE_DIR = Path(__file__).resolve().parents[2]


DB_PATH = BASE_DIR / "data" / "db" / "rag.db"


def get_connection():
    """
    Retourne une connexion SQLite prête à l'emploi.
    Active les foreign keys et permet un accès par nom de colonne.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn