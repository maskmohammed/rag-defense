from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

# Dossiers principaux
FRONTEND_DIR = BASE_DIR / "frontend"
DATA_DIR = BASE_DIR / "data"
DB_DIR = DATA_DIR / "db"
DOCS_DIR = DATA_DIR / "docs" / "demo"
INDEX_DIR = DATA_DIR / "index" / "vector_store"
LOGS_DIR = DATA_DIR / "logs"

DB_PATH = DB_DIR / "rag.db"

# Flask
SECRET_KEY = "rag-defense-pfe-secret-key"

# Upload
ALLOWED_EXTENSIONS = {"txt", "docx", "pdf"}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB


def ensure_project_dirs():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

# LLM local
LLM_ENABLED = True
LLM_PROVIDER = "ollama"
LLM_BASE_URL = "http://127.0.0.1:11434"
LLM_MODEL = "llama3"
LLM_TIMEOUT_SECONDS = 300

