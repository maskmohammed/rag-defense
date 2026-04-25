import json
from db.connection import get_connection


def insert_query_log(user_id: int, question: str, used_documents: list):
    """
    Enregistre une requête dans query_logs.
    used_documents est stocké en JSON texte.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO query_logs (user_id, question, used_documents, created_at)
            VALUES (?, ?, ?, datetime('now'))
            """,
            (
                user_id,
                question.strip(),
                json.dumps(used_documents or [], ensure_ascii=False)
            )
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_recent_logs(limit: int = 50):
    """
    Retourne les logs les plus récents avec username si disponible.
    """
    limit = max(1, min(int(limit), 200))

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                q.id,
                q.user_id,
                u.username,
                q.question,
                q.used_documents,
                q.created_at
            FROM query_logs q
            LEFT JOIN users u ON q.user_id = u.id
            ORDER BY q.created_at DESC, q.id DESC
            LIMIT ?
            """,
            (limit,)
        )
        rows = cursor.fetchall()

        result = []
        for row in rows:
            try:
                used_documents = json.loads(row["used_documents"]) if row["used_documents"] else []
            except json.JSONDecodeError:
                used_documents = []

            result.append({
                "id": row["id"],
                "user_id": row["user_id"],
                "username": row["username"],
                "question": row["question"],
                "used_documents": used_documents,
                "created_at": row["created_at"]
            })

        return result
    finally:
        conn.close()