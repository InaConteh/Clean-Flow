import os

from flask import Flask

from app.config import config_by_name
from app.extensions import cors, db, jwt, limiter, migrate


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__)
    env = config_name or os.getenv("FLASK_ENV", "development")
    app.config.from_object(config_by_name.get(env, config_by_name["default"]))

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": os.getenv("CORS_ORIGINS", "*")}})
    limiter.init_app(app)

    from app.routes import api_bp
    from app.routes.analytics import analytics_bp

    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(analytics_bp, url_prefix="/api")

    @app.route("/health")
    def health():
        return {"status": "ok", "service": "cleanflow-api"}

    return app
