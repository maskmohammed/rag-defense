from functools import wraps
from flask import session, jsonify


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({
                "status": "error",
                "message": "Authentification requise"
            }), 401
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({
                "status": "error",
                "message": "Authentification requise"
            }), 401

        if session.get("role") != "ADMIN":
            return jsonify({
                "status": "error",
                "message": "Accès interdit"
            }), 403

        return f(*args, **kwargs)
    return decorated_function