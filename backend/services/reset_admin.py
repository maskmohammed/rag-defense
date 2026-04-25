from db.connection import get_connection


def reset_admin():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username = ?", ("admin",))
        conn.commit()
        print("Utilisateur admin supprimé")
    finally:
        conn.close()


if __name__ == "__main__":
    reset_admin()