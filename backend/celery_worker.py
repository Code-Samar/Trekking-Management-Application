"""
Celery worker entrypoint.

Run with (from backend/ folder, with venv activated and Redis running):
    celery -A celery_worker.celery worker --loglevel=info --pool=solo   (Windows/Mac dev)
    celery -A celery_worker.celery worker --loglevel=info               (Linux)

Run the beat scheduler (for daily reminders + monthly report) separately:
    celery -A celery_worker.celery beat --loglevel=info
"""
from celery.schedules import crontab
from app import create_app
from extensions import celery_app as celery

flask_app = create_app()


class ContextTask(celery.Task):
    """Ensure every Celery task runs inside the Flask app context so it can
    use the DB, cache, and config exactly like a normal request."""
    def __call__(self, *args, **kwargs):
        with flask_app.app_context():
            return self.run(*args, **kwargs)


celery.Task = ContextTask
celery.conf.update(
    broker_connection_retry_on_startup=True,
)

celery.conf.beat_schedule = {
    "daily-trek-reminders": {
        "task": "tasks.send_daily_reminders",
        "schedule": crontab(minute="*"),  # every day at 08:00
    },
    "monthly-activity-report": {
        "task": "tasks.send_monthly_report",
        "schedule": crontab(day_of_month=1, hour=6, minute=0),  # 1st of every month
    },
}

# Import tasks so Celery registers them against this app instance
import tasks  # noqa: E402,F401
