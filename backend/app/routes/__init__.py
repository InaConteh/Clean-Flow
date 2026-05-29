from flask import Blueprint

api_bp = Blueprint("api", __name__)

from app.routes import sources, reports, sms, tips, auth, repairs  # noqa: E402, F401
