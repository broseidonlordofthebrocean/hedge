"""Celery application configuration."""

from celery import Celery
from celery.schedules import crontab

from ..config import get_settings

settings = get_settings()

celery_app = Celery(
    "hedge",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.tasks.scoring",
        "app.tasks.ingestion",
        "app.tasks.alerts",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/New_York",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    worker_prefetch_multiplier=1,
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "daily-scoring-run": {
        "task": "app.tasks.scoring.run_daily_scoring",
        "schedule": crontab(hour=6, minute=0),  # 6 AM ET
    },
    "ingest-macro-data": {
        "task": "app.tasks.ingestion.ingest_macro_data",
        "schedule": crontab(minute=0),  # Every hour
    },
    "ingest-market-data": {
        "task": "app.tasks.ingestion.ingest_market_data",
        "schedule": crontab(minute="*/15"),  # Every 15 minutes
    },
    "check-alerts": {
        "task": "app.tasks.alerts.check_alerts",
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
    },
}
