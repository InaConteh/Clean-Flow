import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgresql://cleanflow:cleanflow@localhost:5432/cleanflow"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)

    AFRICASTALKING_USERNAME = os.getenv("AFRICASTALKING_USERNAME", "")
    AFRICASTALKING_API_KEY = os.getenv("AFRICASTALKING_API_KEY", "")
    AFRICASTALKING_SHORTCODE = os.getenv("AFRICASTALKING_SHORTCODE", "")

    WEATHER_API_URL = os.getenv("WEATHER_API_URL", "")
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")

    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

    REPAIR_DEFAULT_ETA_HOURS = int(os.getenv("REPAIR_DEFAULT_ETA_HOURS", "48"))

    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "test-secret-key-for-testing-only-32b"
    # Disable rate-limiter storage warnings in tests
    RATELIMIT_ENABLED = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
