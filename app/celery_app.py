"""
Celery Application Configuration
Background task processing for PuneRakshak monitoring engine.
"""
from celery import Celery
from celery.schedules import crontab
import os

# Redis connection URL
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Create Celery app
celery_app = Celery(
    'punerakshak',
    broker=REDIS_URL,
    backend=REDIS_URL
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Kolkata',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,  # 30 minutes max
    task_soft_time_limit=1500,  # 25 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

# Celery Beat Schedule - Run monitoring every hour at minute 0
celery_app.conf.beat_schedule = {
    'hourly-monitoring-cycle': {
        'task': 'app.tasks.monitoring_tasks.run_hourly_monitoring_cycle',
        'schedule': crontab(minute=0),  # Every hour at :00
        'options': {
            'expires': 3300,  # Expire after 55 minutes (before next run)
        }
    },
}

# Task routes
celery_app.conf.task_routes = {
    'app.tasks.monitoring_tasks.*': {'queue': 'monitoring'},
}
