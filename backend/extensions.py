from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_caching import Cache
from celery import Celery

db = SQLAlchemy()
jwt = JWTManager()
cache = Cache()

# Celery instance is created here and configured in celery_worker.py / app factory
celery_app = Celery(__name__)
