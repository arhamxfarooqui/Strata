"""
Celery application configuration — RabbitMQ broker, Redis result backend,
at-least-once delivery, dead-letter queue.
"""

from celery import Celery
from celery.schedules import crontab

from app.config import get_settings

settings = get_settings()

celery_app = Celery("strata")

celery_app.conf.update(
    broker_url=settings.RABBITMQ_URL,
    result_backend=settings.REDIS_URL.replace("/0", "/1"),  # Use DB 1 for results
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Kolkata",
    enable_utc=True,
    # At-least-once delivery: ack AFTER task completes, not before
    task_acks_late=True,
    # If worker crashes mid-task, requeue the message
    task_reject_on_worker_lost=True,
    # Fair dispatch: one task at a time per worker
    worker_prefetch_multiplier=1,
    # Dead-letter queue configuration
    task_default_queue="default",
    task_routes={
        "app.tasks.cf_sync.*": {"queue": "default"},
        "app.tasks.rating_sync.*": {"queue": "default"},
    },
    # Beat schedule for periodic tasks
    beat_schedule={
        "sync-codeforces-upsolves-every-4h": {
            "task": "app.tasks.cf_sync.sync_all_users_upsolves",
            "schedule": crontab(minute=0, hour="*/4"),
        },
        "sync-global-ratings-daily": {
            "task": "app.tasks.rating_sync.sync_global_ratings",
            "schedule": crontab(minute=0, hour=0),
        },
    },
)

# Auto-discover tasks in the tasks package
celery_app.autodiscover_tasks(["app.tasks"])
