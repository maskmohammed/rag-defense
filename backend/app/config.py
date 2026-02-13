from pathlib import Path

# Chemin racine : rag-defense-pfe/
BASE_DIR = Path(__file__).resolve().parents[2]

# Dossiers principaux
FRONTEND_DIR = BASE_DIR / "frontend"
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "db" / "rag.db"
