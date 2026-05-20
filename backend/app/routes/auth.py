from flask import jsonify, request
from flask_jwt_extended import create_access_token, jwt_required

from app.routes import api_bp


@api_bp.route("/auth/login", methods=["POST"])
def login():
    """Admin portal login (scaffold — replace with real user store)."""
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")
    if username == "admin" and password == "admin":
        token = create_access_token(identity=username)
        return jsonify({"access_token": token})
    return jsonify({"error": "Invalid credentials"}), 401


@api_bp.route("/auth/me", methods=["GET"])
@jwt_required()
def me():
    return jsonify({"status": "authenticated"})
