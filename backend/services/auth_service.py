from werkzeug.security import generate_password_hash, check_password_hash
from db.connection import get_connection


def get_user_by_username(username: str):
    """
    Retourne un utilisateur par son nom d'utilisateur.
    Si l'utilisateur n'existe pas, retourne None.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        user = cursor.fetchone()
        return user
    finally:
        conn.close()


def create_user(username: str, password: str, role: str):
    """
    Crée un nouvel utilisateur avec mot de passe hashé.
    Role autorisé : ADMIN ou USER
    """
    if role not in ("ADMIN", "USER"):
        raise ValueError("Rôle invalide")

    password_hash = generate_password_hash(password)

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (username, password_hash, role, created_at)
            VALUES (?, ?, ?, datetime('now'))
            """,
            (username, password_hash, role)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def verify_user_password(username: str, password: str):
    """
    Vérifie qu'un utilisateur existe et que le mot de passe est correct.
    Retourne l'utilisateur si succès, sinon None.
    """
    user = get_user_by_username(username)

    if user is None:
        return None

    if check_password_hash(user["password_hash"], password):
        return user

    return None