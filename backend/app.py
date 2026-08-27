import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

from config import Config
from extensions import db, jwt, cache, celery_app


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(os.path.join(os.path.dirname(__file__), "instance"), exist_ok=True)
    os.makedirs(app.config["EXPORT_DIR"], exist_ok=True)
    os.makedirs(app.config["REPORT_DIR"], exist_ok=True)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Configure Celery's broker/backend here so that ANY process that builds
    # this Flask app - the web server, the celery worker, or a one-off script -
    # talks to the same Redis broker. Without this, calling task.delay() from
    # the Flask process falls back to Celery's default (AMQP) broker and
    # fails, even though the worker itself is correctly wired to Redis.
    celery_app.conf.update(
        broker_url=app.config["CELERY_BROKER_URL"],
        result_backend=app.config["CELERY_RESULT_BACKEND"],
        timezone="Asia/Kolkata",
        enable_utc=True,
        broker_connection_retry_on_startup=True,
    )

    db.init_app(app)
    jwt.init_app(app)

    # Cache: fall back to SimpleCache (in-memory) if Redis isn't reachable,
    # so the app still runs locally even without Redis started yet.
    try:
        cache.init_app(app)
        with app.app_context():
            cache.set("healthcheck", "ok", timeout=5)
    except Exception:
        app.config["CACHE_TYPE"] = "SimpleCache"
        cache.init_app(app)

    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.staff import staff_bp
    from routes.user import user_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(user_bp)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/api/downloads/exports/<path:filename>")
    def download_export(filename):
        return send_from_directory(app.config["EXPORT_DIR"], filename, as_attachment=True)

    @app.get("/api/downloads/reports/<path:filename>")
    def download_report(filename):
        return send_from_directory(app.config["REPORT_DIR"], filename, as_attachment=True)

    with app.app_context():
        db.create_all()
        _ensure_admin_exists(app)

    return app


def _ensure_admin_exists(app):
    """Create the single Admin account programmatically if it doesn't exist yet.
    There is no admin registration endpoint anywhere in the app."""
    from models import User

    existing = User.query.filter_by(role="admin").first()
    if existing:
        return

    admin = User(
        name=app.config["ADMIN_NAME"],
        email=app.config["ADMIN_EMAIL"],
        role="admin",
        status="active",
    )
    admin.set_password(app.config["ADMIN_PASSWORD"])
    db.session.add(admin)
    db.session.commit()
    print(f"[SETUP] Admin created -> email: {app.config['ADMIN_EMAIL']}  password: {app.config['ADMIN_PASSWORD']}")


if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(debug=True, port=5001)
