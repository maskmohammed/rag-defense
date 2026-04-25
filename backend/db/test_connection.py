from db.connection import get_connection


def test_db():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        print("Connexion OK")
        for table in tables:
            print("-", table["name"])
    finally:
        conn.close()


if __name__ == "__main__":
    test_db()