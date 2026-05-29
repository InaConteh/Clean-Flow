from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request

def role_required(allowed_roles):
    """
    Decorator to restrict access to users with specific roles.
    Expects 'role' to be present in JWT claims.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get("role")

            if user_role not in allowed_roles:
                return jsonify({"error": "Insufficient permissions"}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator
