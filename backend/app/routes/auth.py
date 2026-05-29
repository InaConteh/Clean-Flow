from flask import jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app.routes import api_bp
from app.models.user import User
from app.extensions import db

@api_bp.route("/auth/login", methods=["POST"])
def login():
    """Admin portal login using real user records."""
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        # Include role in the access token claims
        token = create_access_token(identity=user.username, additional_claims={"role": user.role})
        return jsonify({
            "access_token": token,
            "role": user.role,
            "preferred_language": user.preferred_language
        })

    return jsonify({"error": "Invalid credentials"}), 401

@api_bp.route("/auth/me", methods=["GET"])
@jwt_required()
def me():
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "username": user.username,
        "role": user.role,
        "preferred_language": user.preferred_language
    })

@api_bp.route("/admin/settings/language", methods=["PATCH"])
@jwt_required()
def update_language():
    """Update preferred language for the dashboard."""
    data = request.get_json(silent=True) or {}
    new_language = data.get("language")

    if not new_language:
        return jsonify({"error": "Language required"}), 400

    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    user.preferred_language = new_language
    db.session.commit()

    return jsonify({
        "message": "Language updated",
        "preferred_language": user.preferred_language
    })
