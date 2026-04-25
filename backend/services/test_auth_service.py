from services.auth_service import create_user, get_user_by_username, verify_user_password


def test_auth():
    try:
        user_id = create_user("admin", "admin123", "ADMIN")
        print(f"Utilisateur créé avec id = {user_id}")
    except Exception as e:
        print("Création ignorée ou erreur :", e)

    user = get_user_by_username("admin")
    if user:
        print("Utilisateur trouvé :", user["username"], "-", user["role"])
    else:
        print("Utilisateur introuvable")

    verified = verify_user_password("admin", "admin")
    if verified:
        print("Mot de passe correct pour :", verified["username"])
    else:
        print("Mot de passe incorrect")


if __name__ == "__main__":
    test_auth()