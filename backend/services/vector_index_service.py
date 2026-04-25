import json
from pathlib import Path
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import INDEX_DIR
from db.connection import get_connection


VECTORIZER_PATH = INDEX_DIR / "tfidf_vectorizer.joblib"
MATRIX_PATH = INDEX_DIR / "chunk_matrix.joblib"
METADATA_PATH = INDEX_DIR / "chunk_metadata.json"


def get_all_chunks():
    """
    Récupère tous les chunks depuis la base avec les métadonnées du document.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                c.id AS chunk_id,
                c.document_id,
                c.chunk_index,
                c.text,
                d.title,
                d.filename,
                d.file_type
            FROM chunks c
            JOIN documents d ON c.document_id = d.id
            ORDER BY c.document_id ASC, c.chunk_index ASC
            """
        )
        rows = cursor.fetchall()
        return rows
    finally:
        conn.close()


def build_vector_index():
    """
    Construit l'index vectoriel local à partir de tous les chunks.
    Sauvegarde :
    - le vectorizer
    - la matrice TF-IDF
    - les métadonnées
    """
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    rows = get_all_chunks()
    if not rows:
        raise ValueError("Aucun chunk disponible pour construire l'index")

    texts = [row["text"] for row in rows]

    vectorizer = TfidfVectorizer( lowercase=True, ngram_range=(1, 2), min_df=1, max_df=0.8)
    matrix = vectorizer.fit_transform(texts)

    metadata = []
    for row in rows:
        metadata.append({
            "chunk_id": row["chunk_id"],
            "document_id": row["document_id"],
            "chunk_index": row["chunk_index"],
            "text": row["text"],
            "title": row["title"],
            "filename": row["filename"],
            "file_type": row["file_type"]
        })

    joblib.dump(vectorizer, VECTORIZER_PATH)
    joblib.dump(matrix, MATRIX_PATH)

    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    return {
        "chunks_indexed": len(metadata),
        "vectorizer_path": str(VECTORIZER_PATH),
        "matrix_path": str(MATRIX_PATH),
        "metadata_path": str(METADATA_PATH)
    }


def load_vector_index():
    """
    Charge l'index vectoriel local depuis le disque.
    """
    if not VECTORIZER_PATH.exists():
        raise FileNotFoundError("Vectorizer introuvable")

    if not MATRIX_PATH.exists():
        raise FileNotFoundError("Matrice introuvable")

    if not METADATA_PATH.exists():
        raise FileNotFoundError("Métadonnées introuvables")

    vectorizer = joblib.load(VECTORIZER_PATH)
    matrix = joblib.load(MATRIX_PATH)

    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    return vectorizer, matrix, metadata


def search_similar_chunks(query: str, top_k: int = 5):
    """
    Recherche les chunks les plus proches d'une requête.
    """
    if not query or not query.strip():
        return []

    vectorizer, matrix, metadata = load_vector_index()

    query_vector = vectorizer.transform([query])
    similarities = cosine_similarity(query_vector, matrix)[0]

    scored_results = []
    for idx, score in enumerate(similarities):
        scored_results.append({
            "score": float(score),
            "metadata": metadata[idx]
        })

    scored_results.sort(key=lambda x: x["score"], reverse=True)

    return scored_results[:top_k]