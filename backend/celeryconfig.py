"""Celery configuration."""

from app.core.config import settings

broker_url = settings.CELERY_BROKER_URL
result_backend = settings.CELERY_RESULT_BACKEND
task_serializer = "json"
accept_content = ["json"]
result_serializer = "json"
timezone = "UTC"
enable_utc = True
task_track_started = True
task_time_limit = 600  # 10 minutes max per task
task_soft_time_limit = 540
worker_prefetch_multiplier = 1
