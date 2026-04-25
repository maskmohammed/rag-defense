from flask import Flask, jsonify, redirect, request, session
from werkzeug.exceptions import RequestEntityTooLarge

from app.config import (
    FRONTEND_DIR,
    SECRET_KEY,
    MAX_CONTENT_LENGTH,
    ensure_project_dirs
)
from services.auth_service import verify_user_password
from utils.auth_decorators import login_required, admin_required
from services.document_service import save_uploaded_file
from services.document_db_service import get_all_documents
from services.rag_service import query_rag
from services.log_service import insert_query_log, get_recent_logs


def create_app():
    ensure_project_dirs()

    app = Flask(
        __name__,
        static_folder=str(FRONTEND_DIR),
        static_url_path="/static"
    )

    app.secret_key = SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

    # ===============================
    # API TEST
    # ===============================
    @app.get("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    # ===============================
    # AUTH
    # ===============================
    @app.post("/auth/login")
    def login():
        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "message": "Requête invalide"
            }), 400

        username = data.get("username", "").strip()
        password = data.get("password", "").strip()

        if not username or not password:
            return jsonify({
                "status": "error",
                "message": "Nom d'utilisateur et mot de passe requis"
            }), 400

        user = verify_user_password(username, password)

        if user is None:
            return jsonify({
                "status": "error",
                "message": "Identifiants invalides"
            }), 401

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["role"] = user["role"]

        return jsonify({
            "status": "success",
            "message": "Connexion réussie",
            "role": user["role"]
        }), 200

    @app.post("/auth/logout")
    def logout():
        session.clear()
        return jsonify({
            "status": "success",
            "message": "Déconnexion réussie"
        }), 200

    @app.get("/auth/me")
    @login_required
    def me():
        return jsonify({
            "status": "success",
            "user": {
                "id": session.get("user_id"),
                "username": session.get("username"),
                "role": session.get("role")
            }
        }), 200

    # ===============================
    # ROUTES FRONTEND
    # ===============================
    @app.get("/")
    def root():
        if "user_id" not in session:
            return redirect("/login")

        if session.get("role") == "ADMIN":
            return redirect("/admin")

        return redirect("/app")

    @app.get("/login")
    def login_page():
        if "user_id" in session:
            if session.get("role") == "ADMIN":
                return redirect("/admin")
            return redirect("/app")

        return app.send_static_file("login.html")

    @app.get("/app")
    @login_required
    def app_page():
        return app.send_static_file("index.html")

    @app.get("/admin")
    @admin_required
    def admin_page():
        return app.send_static_file("admin.html")

    # ===============================
    # ROUTE TEST ADMIN
    # ===============================
    @app.get("/admin/test")
    @admin_required
    def admin_test():
        return jsonify({
            "status": "success",
            "message": "Accès ADMIN autorisé"
        }), 200

    # ===============================
    # DOCUMENTS - UPLOAD
    # ===============================
    @app.post("/documents/upload")
    @admin_required
    def upload_document():
        if "file" not in request.files:
            return jsonify({
                "status": "error",
                "message": "Aucun fichier fourni"
            }), 400

        file = request.files["file"]

        try:
            result = save_uploaded_file(file)

            return jsonify({
                "status": "success",
                "message": "Fichier uploadé, ingéré et indexé avec succès",
                "filename": result["filename"],
                "path": result["file_path"],
                "document_id": result["document_id"],
                "chunks": result["chunks"]
            }), 201

        except ValueError as e:
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 400

        except Exception:
            return jsonify({
                "status": "error",
                "message": "Erreur lors de l'upload"
            }), 500

    # ===============================
    # DOCUMENTS - GET ALL
    # ===============================
    @app.get("/documents")
    @admin_required
    def list_documents():
        documents = get_all_documents()

        result = []
        for doc in documents:
            result.append({
                "id": doc["id"],
                "title": doc["title"],
                "filename": doc["filename"],
                "file_type": doc["file_type"],
                "imported_at": doc["imported_at"]
            })

        return jsonify({
            "status": "success",
            "documents": result
        }), 200

    # ===============================
    # RAG - QUERY
    # ===============================
    @app.post("/query")
    @login_required
    def query():
        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "message": "Requête invalide"
            }), 400

        question = data.get("question", "").strip()

        if not question:
            return jsonify({
                "status": "error",
                "message": "Question requise"
            }), 400

        try:
            result = query_rag(question, top_k=5)

            used_documents = result.get("sources", [])
            insert_query_log(
                user_id=session.get("user_id"),
                question=question,
                used_documents=used_documents
            )

            return jsonify(result), 200

        except FileNotFoundError:
            return jsonify({
                "status": "error",
                "message": "Index vectoriel introuvable"
            }), 500

        except ValueError as e:
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 400

        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Erreur lors de la requête: {str(e)}"
            }), 500

    # ===============================
    # LOGS - ADMIN
    # ===============================
    @app.get("/logs")
    @admin_required
    def logs():
        try:
            raw_limit = request.args.get("limit", "50").strip()
            limit = int(raw_limit)

            logs_data = get_recent_logs(limit=limit)

            return jsonify({
                "status": "success",
                "logs": logs_data,
                "count": len(logs_data)
            }), 200

        except ValueError:
            return jsonify({
                "status": "error",
                "message": "Paramètre limit invalide"
            }), 400

        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Erreur lors du chargement des logs: {str(e)}"
            }), 500

    # ===============================
    # ERRORS
    # ===============================
    @app.errorhandler(RequestEntityTooLarge)
    def file_too_large(e):
        return jsonify({
            "status": "error",
            "message": "Fichier trop volumineux"
        }), 413

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "status": "error",
            "message": "Route non trouvée"
        }), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({
            "status": "error",
            "message": "Erreur interne serveur"
        }), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=8000, debug=True)