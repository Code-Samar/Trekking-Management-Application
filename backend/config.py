import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = "tma-dev-secret-key-change-in-prod"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'tma.sqlite3')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = "tma-dev-jwt-secret-change-in-prod"
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 8  # 8 hours

    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_HOST = "localhost"
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = 0
    CACHE_DEFAULT_TIMEOUT = 60

    CELERY_BROKER_URL = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/2"

    # Admin bootstrap credentials (only used the first time DB is created)
    ADMIN_EMAIL = "admin@tma.com"
    ADMIN_PASSWORD = "Admin@123"
    ADMIN_NAME = "System Admin"

    # Mail (used by Celery tasks - mock/logged in dev unless SMTP configured)
    MAIL_ENABLED = False
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USERNAME = os.environ.get("TMA_MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("TMA_MAIL_PASSWORD", "")

    EXPORT_DIR = os.path.join(BASE_DIR, "exports")
    REPORT_DIR = os.path.join(BASE_DIR, "reports")
