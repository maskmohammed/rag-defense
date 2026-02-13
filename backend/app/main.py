from flask import Flask, jsonify, send_from_directory, redirect
from app.config import FRONTEND_DIR


def create_app():
    app = Flask(
        __name__,
        static_folder=str(FRONTEND_DIR),
        static_url_path="/static"
    )

    # ===============================
    # API TEST
    # ===============================
    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    # ===============================
    # ROUTES FRONTEND
    # ===============================
    @app.get("/")
    def root():
        return redirect("/login")

    @app.get("/login")
    def login_page():
        return send_from_directory(FRONTEND_DIR, "login.html")

    @app.get("/app")
    def app_page():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.get("/admin")
    def admin_page():
        return send_from_directory(FRONTEND_DIR, "admin.html")

    # ===============================
    # STATIC FILES (JS + CSS)
    # ===============================
    @app.get("/static/<path:filename>")
    def static_files(filename):
        return send_from_directory(FRONTEND_DIR, filename)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=8000, debug=True)
