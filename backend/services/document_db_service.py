from db.connection import get_connection


def insert_document(title: str, filename: str, file_type: str):
    """
    Insère un document dans la table documents.
    Retourne l'id du document créé.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO documents (title, filename, file_type, imported_at)
            VALUES (?, ?, ?, datetime('now'))
            """,
            (title, filename, file_type.upper())
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def insert_chunks(document_id: int, chunks: list):
    """
    Insère plusieurs chunks liés à un document.
    vector_id est provisoirement vide ou généré localement.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        for chunk in chunks:
            vector_id = f"doc{document_id}_chunk{chunk['chunk_index']}"

            cursor.execute(
                """
                INSERT INTO chunks (document_id, chunk_index, text, vector_id)
                VALUES (?, ?, ?, ?)
                """,
                (
                    document_id,
                    chunk["chunk_index"],
                    chunk["text"],
                    vector_id
                )
            )

        conn.commit()
    finally:
        conn.close()


def get_all_documents():
    """
    Retourne tous les documents importés.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM documents
            ORDER BY imported_at DESC
            """
        )
        return cursor.fetchall()
    finally:
        conn.close()


def get_chunks_by_document_id(document_id: int):
    """
    Retourne tous les chunks d'un document.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM chunks
            WHERE document_id = ?
            ORDER BY chunk_index ASC
            """,
            (document_id,)
        )
        return cursor.fetchall()
    finally:
        conn.close()